init:
	pip install -e .[gs,event]

clean:
	find . -name '*.pyc' -delete

format: clean
	black ricloud/

test: clean
	pytest tests/

.PHONY: init clean test
