SHELL := /bin/bash
verbosity=1

#########################################
# bumpversion Usage
#########################################
# `bumpversion [major|minor|patch|build]`
# `bumpversion --tag release

update_dist:
	python setup.py sdist bdist_wheel

check_dist:
	twine check dist/*-$(v)*

upload_test:
	twine upload --repository testpypi dist/*-$(v)*

upload:
	twine upload dist/*-$(v)*