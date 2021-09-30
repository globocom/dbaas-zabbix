.PHONY: clean-pyc clean-build docs clean

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "test-all - run tests on every Python version with tox"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "release - package and upload a release"
	@echo "dist - package"

clean: clean-build clean-pyc
	rm -fr htmlcov/

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

lint:
	flake8 dbaas_zabbix tests

test:
	py.test -v  tests/

test-all:
	tox

coverage:
	coverage run --source dbaas_zabbix setup.py test

docs:
	rm -f docs/dbaas-zabbix.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ dbaas-zabbix
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	open docs/_build/html/index.html

release:
	python setup.py sdist bdist_wheel
	twine upload dist/*

release_globo:
	python setup.py sdist bdist_wheel
	twine upload --repository-url https://artifactory.globoi.com/artifactory/api/pypi/pypi-local dist/*

fake_deploy:
	rm -f /Users/$(USER)/.virtualenvs/dbaas/lib/python2.7/site-packages/dbaas_zabbix/__init__.pyc
	rm -f /Users/$(USER)/.virtualenvs/dbaas/lib/python2.7/site-packages/dbaas_zabbix/database_providers.pyc
	rm -f /Users/$(USER)/.virtualenvs/dbaas/lib/python2.7/site-packages/dbaas_zabbix/dbaas_api.pyc
	rm -f /Users/$(USER)/.virtualenvs/dbaas/lib/python2.7/site-packages/dbaas_zabbix/provider.pyc
	rm -f /Users/$(USER)/.virtualenvs/dbaas/lib/python2.7/site-packages/dbaas_zabbix/provider_factory.pyc
	cp dbaas_zabbix/__init__.py /Users/$(USER)/.virtualenvs/dbaas/lib/python2.7/site-packages/dbaas_zabbix/
	cp dbaas_zabbix/database_providers.py /Users/$(USER)/.virtualenvs/dbaas/lib/python2.7/site-packages/dbaas_zabbix/
	cp dbaas_zabbix/dbaas_api.py /Users/$(USER)/.virtualenvs/dbaas/lib/python2.7/site-packages/dbaas_zabbix/
	cp dbaas_zabbix/provider.py /Users/$(USER)/.virtualenvs/dbaas/lib/python2.7/site-packages/dbaas_zabbix/
	cp dbaas_zabbix/provider_factory.py /Users/$(USER)/.virtualenvs/dbaas/lib/python2.7/site-packages/dbaas_zabbix/

dist: clean
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist
