import logging
import os
import re
import secrets
import time
from typing import Dict, List, Union
from io import StringIO, TextIOWrapper, BytesIO

import requests

from .base import DuetAPI

#: Start of the line send_code echoes after each code to find the end of its reply.
REPLY_MARKER_PREFIX = '__dwa:'

#: Codes that switch the channel into writing to a file: M28 until an M29, M559 and
#: M560 until the upload is complete. Every line after one is written into the file
#: rather than run, the reply marker included, so the marker would never come back
#: and would end up in the file.
_FILE_WRITE = re.compile(r'(?mi)^\s*(?:N\d+\s+)?M(?:28|559|560)(?![\d.])')

#: Codes that can never be answered. M112 aborts every input channel, the one it
#: arrived on included; M999 restarts the board. Not M999 B<n> for another board, nor
#: M999 A<n>, which flashes a PanelDue: the main board replies to both.
_NEVER_REPLIES = re.compile(
    r'(?mi)^\s*(?:N\d+\s+)?(?:M112(?![\d.])|M999(?![\d.])(?![^;\n]*\s(?:A|B\s*0*[1-9])))')

#: M122 with nothing after it but a comment. RegularGCodeInput::CheckForUrgentCommand
#: spots it as the characters arrive, takes it out of the input and asks the main task
#: for RepRap::DeferredDiagnostics instead, so it never runs in its place on the
#: channel. The report is generated at the end of the main loop pass that has just run
#: the marker after it, so it lands in the buffer *after* the marker. Measured on an
#: MB6HC: the marker, then 3.6 kB of diagnostics, in one fetch. Anything after the
#: 122 but a control character or ';' -- a space included -- makes it an ordinary
#: code, as does a line number, since the scanner only looks at the start of a line.
_URGENT_DIAGNOSTICS = re.compile(r'(?mi)^[ \t]*M122(?=[\x00-\x1f;]|$)')


def _merge_reply(text: str, fetched: str) -> str:
    """ Add one rr_reply fetch to the text collected so far.

    RepRapFirmware keeps a reply until every session has fetched it, so with
    another client connected (a browser running DWC, say) a fetch returns the
    whole buffer again, grown, rather than just what is new.
    """
    if fetched.startswith(text):
        return fetched
    return text + fetched


def _reply_before(text: str, marker: str) -> str:
    """ The part of the reply buffer that belongs to the code ending at marker.

    A buffer kept for another session can still hold earlier codes' replies, each
    ended by its own marker, so start after the last of those.
    """
    reply = text[:text.index(marker)]
    earlier = reply.rfind(REPLY_MARKER_PREFIX)
    if earlier >= 0:
        line_end = reply.find('\n', earlier)
        reply = reply[line_end + 1:] if line_end >= 0 else ''
    return reply


class DWCAPI(DuetAPI):
    """
    Duet Web Control REST API Interface.

    Used with a Duet 2/3 in standalone mode.
    Must use RRF3.
    """
    api_name = 'DWC_REST'

    def connect(self, password=''):
        """ Start connection to Duet """
        url = f'{self.base_url}/rr_connect'
        r = self.session.get(url, params={'password': password})
        if not r.ok:
            raise ValueError
        return r.json()

    def disconnect(self):
        """ End connection to Duet """
        url = f'{self.base_url}/rr_disconnect'
        r = self.session.get(url)
        if not r.ok:
            raise ValueError
        return r.json()

    def get_model(self, key: str = None, depth: int = 99, verbose: bool = True, null: bool = True, frequent: bool = False, obsolete: bool = False) -> Dict:
        url = f'{self.base_url}/rr_model'
        flags = f'd{depth}'
        flags += 'v' if verbose is True else ''
        flags += 'n' if null is True else ''
        flags += 'f' if frequent is True else ''
        flags += 'o' if obsolete is True else ''
        r = self.session.get(url, params={'flags': flags, 'key': key})
        if not r.ok:
            raise ValueError
        j = r.json()
        return j['result']

    def _get_reply(self) -> str:
        url = f'{self.base_url}/rr_reply'
        r = self.session.get(url)
        if not r.ok:
            raise ValueError
        return r.text

    def _get_reply_seq(self) -> int:
        """ Sequence number of the most recent G-code reply.

        RepRapFirmware bumps HttpResponder::seq every time a reply is added to the
        buffer and exposes it as seqs.reply. Polling it is the only way to know that
        a reply belongs to the code you just sent, because rr_gcode is asynchronous
        and rr_reply returns the accumulated text with no correlation id.

        flags=f restricts the response to live fields, which is the cheap poll DWC
        itself uses.
        """
        url = f'{self.base_url}/rr_model'
        r = self.session.get(url, params={'key': 'seqs', 'flags': 'd2f'})
        if not r.ok:
            raise ValueError
        return r.json()['result']['reply']

    def send_code(self, code: str, timeout: float = 30, poll_interval: float = 0.02, wait: bool = True) -> Dict:
        """ Send G/M/T-code to Duet and return its reply.

        rr_gcode only queues the code and returns immediately, and rr_reply hands
        back whatever has accumulated with nothing to say which code it belongs to.
        Waiting for seqs.reply to move is not enough to tell: it moves for every
        message sent to the HTTP channel, including asynchronous ones such as a
        driver warning, so one of those arriving mid-move ends the wait early. The
        code is then treated as finished while it is still running, and every reply
        after it is attributed to the code before.

        So the code is followed, in the same request, by an echo of a marker unique
        to this call. The HTTP channel runs its codes in order, so the marker can
        only be echoed once the code has finished -- macros, M400 and all -- and
        everything before it in the reply buffer is the code's reply. Asynchronous
        messages that arrive while the code runs are still included, since nothing
        distinguishes them from the code's own output.

        The exception is a code that starts writing to a file (M28, M559, M560):
        everything after it on the channel goes into the file, the marker included.
        Those fall back to waiting for seqs.reply to move.

        A bare M122 is run out of band, and its report lands after the marker rather
        than before it (see _URGENT_DIAGNOSTICS). So once that marker is back a second
        one is sent: it can only be echoed after the report, and the reply is
        everything before the first marker and between the two.

        wait=False skips the wait entirely, for codes that deliberately never reply
        because they reset the board. M112 and M999 are recognised and never waited
        for whatever wait says, since waiting for them can only time out.
        """
        if not wait or _NEVER_REPLIES.search(code):
            self._queue_gcode(code)
            return {'response': '', 'seq': None}
        if _FILE_WRITE.search(code):
            return self._send_unmarked(code, timeout, poll_interval)

        deadline = time.monotonic() + timeout
        marker = f'{REPLY_MARKER_PREFIX}{secrets.token_hex(6)}'
        seq = self._get_reply_seq()
        self._queue_gcode(f'{code}\necho "{marker}"', code)
        text, seq = self._wait_for_marker(marker, '', seq, code, deadline, timeout, poll_interval)
        response = _reply_before(text, marker)

        if _URGENT_DIAGNOSTICS.search(code):
            after = f'{REPLY_MARKER_PREFIX}{secrets.token_hex(6)}'
            self._queue_gcode(f'echo "{after}"', code)
            text, seq = self._wait_for_marker(after, text, seq, code, deadline, timeout, poll_interval)
            response += _reply_before(text, after)

        return {'response': response, 'seq': seq}

    def _wait_for_marker(self, marker: str, text: str, seq: int, code: str,
                         deadline: float, timeout: float, poll_interval: float):
        """ Collect the reply buffer until marker is in it. Returns the text and seq. """
        while True:
            latest = self._get_reply_seq()
            # Compared with != rather than > because seq is a uint16 and wraps.
            if latest != seq:
                seq = latest
                text = _merge_reply(text, self._get_reply())
                if marker in text:
                    return text, seq
            if time.monotonic() >= deadline:
                raise TimeoutError(f'No reply to {code!r} after {timeout}s')
            time.sleep(poll_interval)

    def _send_unmarked(self, code: str, timeout: float, poll_interval: float) -> Dict:
        """ Send a code that starts writing to a file, and wait for its reply.

        No marker can follow it (see _FILE_WRITE), so this falls back to waiting for
        seqs.reply to move. That can be fooled by an asynchronous message, but these
        codes reply as soon as the file is opened, so the window for one is small.
        """
        seq = self._get_reply_seq()
        self._queue_gcode(code)
        deadline = time.monotonic() + timeout
        while True:
            latest = self._get_reply_seq()
            # Compared with != rather than > because seq is a uint16 and wraps.
            if latest != seq:
                return {'response': self._get_reply(), 'seq': latest}
            if time.monotonic() >= deadline:
                raise TimeoutError(f'No reply to {code!r} after {timeout}s')
            time.sleep(poll_interval)

    def _queue_gcode(self, gcode: str, code: str = None) -> None:
        url = f'{self.base_url}/rr_gcode'
        r = self.session.get(url, params={'gcode': gcode})
        if not r.ok:
            raise ValueError
        if r.json().get('err'):
            raise ValueError(f'Duet did not accept the code (buffer full, or too long): {code or gcode!r}')

    def get_file(self, filename: str, directory: str = 'gcodes', binary: bool = False) -> str:
        """
        filename: name of the file you want to download including extension
        directory: the folder that the file is in, options are ['gcodes', 'macros', 'sys']
        binary: return binary data instead of a string

        returns the file as a string or binary data
        """
        url = f'{self.base_url}/rr_download'
        r = self.session.get(url, params={'name': f'/{directory}/{filename}'})
        if not r.ok:
            raise ValueError
        if binary:
            return r.content
        else:
            return r.text

    def upload_file(self, file: Union[str, bytes, StringIO, TextIOWrapper, BytesIO], filename: str, directory: str = 'gcodes') -> Dict:
        url = f'{self.base_url}/rr_upload?name=/{directory}/{filename}'
        r = self.session.post(url, data=file)
        if not r.ok:
            raise ValueError
        return r.json()

    def get_fileinfo(self, filename: str = None, directory: str = 'gcodes') -> Dict:
        url = f'{self.base_url}/rr_fileinfo'
        if filename:
            r = self.session.get(url, params={'name': f'/{directory}/{filename}'})
        else:
            r = self.session.get(url)
        if not r.ok:
            raise ValueError
        return r.json()

    def delete_file(self, filename: str, directory: str = 'gcodes') -> Dict:
        url = f'{self.base_url}/rr_delete'
        r = self.session.get(url, params={'name': f'/{directory}/{filename}'})
        if not r.ok:
            raise ValueError
        return r.json()

    def move_file(self, from_path, to_path, **_ignored):
        # BUG this doesn't work currently
        raise NotImplementedError
        url = f'{self.base_url}/rr_move'
        r = self.session.get(url, params={'old': f'{from_path}', 'new': f'{to_path}'})
        if not r.ok:
            raise ValueError
        return r.json()

    def get_directory(self, directory: str) -> List[Dict]:
        url = f'{self.base_url}/rr_filelist'
        r = self.session.get(url, params={'dir': f'/{directory}'})
        if not r.ok:
            raise ValueError
        return r.json()['files']

    def create_directory(self, directory: str) -> Dict:
        url = f'{self.base_url}/rr_mkdir'
        r = self.session.get(url, params={'dir': f'/{directory}'})
        if not r.ok:
            raise ValueError
        return r.json()
