include include/Common.mk
include include/Python.mk

SRC ?= src
TESTS = $(SRC)/lamr.py

.PHONY: release
release: ## Run tests and tag new release
	$(MAKE) test lint && poetry run bumpver update

.PHONY: local-sync
local-sync: ## Copy lamr to ~/.local/bin
	cp src/lamr.py ~/.local/bin/lamr
