init:
	pip install -r requirements.txt

init-dev:
	pip install -r requirements-local.txt

test:
	find . -name '*.pyc' -delete
	py.test tests

.PHONY: init test
