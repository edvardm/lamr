AUTOFLAKE_FLAGS = --remove-unused-variables --ignore-init-module-imports --recursive
BLACK_FLAGS = --color
ISORT_FLAGS = --profile black --quiet

MYPY_FLAGS = --ignore-missing-imports --pretty
POETRY_FLAGS = --remove-untracked --no-interaction

VENV ?= .venv
TIMEOUT ?= 3
TESTS = tests
PYTEST_CMD = poetry run python -m pytest --color yes

# in CI, don't modify things, check only
ifdef CI
	AUTOFLAKE_FLAGS += --check
	ISORT_FLAGS += --check
	BLACK_FLAGS += --diff --check
else
	AUTOFLAKE_FLAGS += --in-place
endif

LINT_CMD = pylint -j0 --fail-under $(MIN_LINTER_SCORE) --output-format colorized

# change these to your liking
SRC ?= src
MIN_LINTER_SCORE = 9.75

### standard rules

lint: pylint yamllint

fmt: autoflake isort
	poetry run black $(BLACK_FLAGS) $(SRC) $(TESTS)

setup: deps .sentinel-setup .envrc

test:
	$(PYTEST_CMD) --timeout $(TIMEOUT) --durations 3 -ra --failed-first -x $(TESTS)

test-cov:
	$(PYTEST_CMD) --timeout 10 --cov $(SRC) --cov-branch $(TESTS)

local-run: setup
	@echo "Setting up project"

clean:
	@find . -type d -name __pycache__ -exec rm -r {} \+
	rm -rf .sentinel*

dist-clean: clean
	rm -rf $(VENV)
### custom rules

.PHONY: deps
deps: .sentinel-deps ## Install dependencies

.PHONY: pylint
pylint:
	$(LINT_CMD) $(SRC)

.PHONY: mypy
mypy: ## Run mypy against source code
	poetry run mypy $(MYPY_FLAGS) $(SRC)

.PHONY: autoflake
autoflake: ## Autoflake source code
	# autoflake is quite noisy, hence uniq :/
	poetry run autoflake $(AUTOFLAKE_FLAGS) $(SRC) $(TESTS) | uniq

.PHONY: isort
isort:  ## isort source code
	poetry run isort $(ISORT_FLAGS) $(SRC)

.PHONY: pyupgrade
pyupgrade: ## Run pyupgrade with fixes applicable for 3.7+
	poetry run pyupgrade --py37-plus `git ls-files | grep \.py`

$(VENV): ## Create local virtual env dir using venv module
	python -m venv $(VENV)
	@echo Remember to do \'source $(VENV)/bin/activate\' to use virtual environment

.sentinel-setup:
	(grep -q pre-commit pyproject.toml && poetry run pre-commit install -t pre-push) || true
	touch $@

.sentinel-deps: poetry.lock
	poetry install $(POETRY_FLAGS)
	touch $@
