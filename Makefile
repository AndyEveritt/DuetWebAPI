SHELL := /bin/bash
verbosity=1

update_dist:
	python setup.py sdist bdist_wheel

check_dist:
	twine check dist/*-$(v)*

upload_test:
	twine upload --repository testpypi dist/*-$(v)*