python := python3.10

.PHONY: run
run:
	uvicorn notes.server:app --reload --host 0.0.0.0 --port 5003

.PHONY: runv2
runv2:
	uvicorn notes_v2.server:app --reload --host 0.0.0.0 --port 5005

.PHONY: test
test:
	$(python) -m pytest -s -vv --asyncio-mode=strict tests

.PHONY: testv2
testv2:
	$(python) -m pytest -s -vv --asyncio-mode=strict tests_v2

.PHONY: create
create:
	$(python) -m notes.database create
