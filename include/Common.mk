# vim: set ft=Makefile

# use sane shell by default, as well as other settings
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables --no-builtin-rules
.DEFAULT_GOAL = help

.PHONY: all
all: help

# Hack to make help rule work, given that rule has suffixe ' ## <help text'.
# Minor adjustments to make it work properly with included files
.PHONY: help
help: ## This help dialog
	@grep -hE '^[a-zA-Z-][a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort -u -t: -k1,1 | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}'

.PHONY: yamllint
yamllint: ## Run yamllint
	(yamllint -f colored .github/**/{*.yaml,*.yml}) || echo "no yaml files found"

.envrc:
	@(test -f .envrc \
		&& (echo ".envrc exists, refusing to overwrite"; exit 0)) \
		|| (test -f dotenvrc-sample && cp dotenvrc-sample .envrc || true)

# It is better to run each test separately in CI, but this should contain
# all rules run by CI, so that if ci-test passes locally, then CI should pass
# too. If you want to just have something that works, you can start with `make ci-test`
# in CI too.
.PHONY: ci-check
ci-check: test-cov lint ## Run all CI tests
	CI=1 $(MAKE) fmt

# Common rules which should exist but implemented in specific files
# (like formatting in Rust.mk, Python.mk etc)

.PHONY: build
build:  ## Build project and/or container image(s)

.PHONY: clean
clean:  ## Clean the repository directory from any generated artifacts

.PHONY: setup
setup: .envrc  ## Prepare project for first run/development

.PHONY: fmt
fmt: 	## Apply all automated formatters

.PHONY: lint
lint:  	## Analyze code for issues/smells

.PHONY: local-run
local-run:  ## Run system locally in bare metal

.PHONY: test-cov
test-cov:  ## Run test code line coverage analysis

.PHONY: test
test: 	## Run all automated tests

.PHONY: docs
docs: 	## Build documentation
