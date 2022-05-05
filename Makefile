python := python3.10

.PHONY: run
run:
	uvicorn server:app --reload --host 0.0.0.0 --port 5003

.PHONY: test
test:
	$(python) -m pytest -s -vv --asyncio-mode=strict tests
