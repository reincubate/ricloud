init:
	pip install -e .

clean:
	find . -name '*.pyc' -delete

test: clean
	pytest tests/

.PHONY: init clean test
