init:
	pip install -e .[gs,event]

init-test:
	pip install -e .[gs,event,test]

init-dev: init
	pip install -r requirements-dev.txt

clean:
	find . -name '*.pyc' -delete

format: clean
	black ricloud/

test: clean
	pytest -m "not integration" tests/

.PHONY: init clean test
