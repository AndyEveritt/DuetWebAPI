import logging
import os
import time
from typing import Dict, List, Union
from io import StringIO, TextIOWrapper, BytesIO

import requests

from .base import DuetAPI


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

        rr_gcode only queues the code and returns immediately, so we note
        seqs.reply first and wait for it to change before fetching rr_reply.
        Without that wait the text returned is whatever happened to be in the
        buffer from an earlier code, or an empty string.

        This is safe for codes that produce no output: GCodes::HandleReplyPreserveResult
        sends a reply for every code that arrived on the HTTP channel, empty or not
        ("DWC expects a reply from every code"), so the sequence number always moves.

        wait=False skips the wait entirely, for codes that deliberately never reply
        because they reset the board -- M999, and M112 followed by M999.
        """
        start_seq = None if not wait else self._get_reply_seq()

        url = f'{self.base_url}/rr_gcode'
        r = self.session.get(url, params={'gcode': code})
        if not r.ok:
            raise ValueError
        if r.json().get('err'):
            raise ValueError(f'Duet did not accept the code (buffer full, or too long): {code!r}')

        if not wait:
            return {'response': '', 'seq': None}

        deadline = time.monotonic() + timeout
        while True:
            seq = self._get_reply_seq()
            # Compared with != rather than > because seq is a uint16 and wraps.
            if seq != start_seq:
                break
            if time.monotonic() >= deadline:
                raise TimeoutError(
                    f'No reply to {code!r} after {timeout}s (seqs.reply stayed at {start_seq})')
            time.sleep(poll_interval)

        return {'response': self._get_reply(), 'seq': seq}

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
