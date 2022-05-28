LINTING_DIRS := notes_v2 tests_v2

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


.PHONY: coverage
coverage:
	poetry run coverage run -m pytest
	poetry run coverage report
	poetry run coverage xml

.PHONY: tox-test
tox-test:
	poetry run tox -vv --parallel --parallel-live

.PHONY: check-isort
check-isort:
	poetry run isort --diff --check-only --settings-path pyproject.toml $(LINTING_DIRS)

.PHONY: check-autoflake
check-autoflake:
	poetry run autoflake --recursive $(LINTING_DIRS)

.PHONY: check-flake8
check-flake8:
	poetry run python -m flake8 $(LINTING_DIRS)

.PHONY: check-mypy
check-mypy:
	poetry run mypy --config-file pyproject.toml $(LINTING_DIRS)


.PHONY: fix-isort
fix-isort:
	poetry run isort --settings-path pyproject.toml $(LINTING_DIRS)

.PHONY: fix-autoflake
fix-autoflake:
	poetry run autoflake --recursive --in-place $(LINTING_DIRS)

.PHONY: check-lint
check-lint:
	$(python) -m no_init --allow-empty $(LINTING_DIRS)
	$(python) -m force_absolute_imports $(LINTING_DIRS)
	$(python) -m isort --check-only --force-single-line-imports $(LINTING_DIRS)
	$(python) -m autoflake --recursive $(LINTING_DIRS)
	$(python) -m autopep8 --diff --recursive --aggressive --ignore=E501,W503,E701,E704,E721,E741,I100,I201,W504 --exclude=musictool/util/wavfile.py $(LINTING_DIRS)
	$(python) -m unify --recursive $(LINTING_DIRS)
	$(python) -m flake8 $(LINTING_DIRS)
	#$(python) -m darglint --docstring-style numpy --verbosity 2 $(LINTING_DIRS)
	#$(python) -m black --diff --check --config pyproject.toml $(LINTING_DIRS)

.PHONY: fix-lint
fix-lint:
	$(python) -m force_absolute_imports --in-place $(LINTING_DIRS)
	$(python) -m isort --force-single-line-imports $(LINTING_DIRS)
	$(python) -m autoflake --recursive --in-place $(LINTING_DIRS)
	$(python) -m autopep8 --in-place --recursive --aggressive --ignore=E501,W503,E701,E704,E721,E741,I100,I201,W504 --exclude=musictool/util/wavfile.py $(LINTING_DIRS)
	$(python) -m unify --recursive --in-place $(LINTING_DIRS)
	trim $(LINTING_DIRS)
	#$(python) -m fixit.cli.apply_fix
