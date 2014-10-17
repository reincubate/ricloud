apps = ricloud

develop:
	pip install -e .
	make install-test-requirements

install-test-requirements:
	pip install "file://`pwd`#egg=ricloud[tests]"

test:
	@echo "Running tests"
	py.test $(apps)
	@echo ""

live-test:
	@echo "Running live tests - these can be slow."
	RUN_LIVE_TESTS=True \
	py.test $(apps)
	@echo ""
