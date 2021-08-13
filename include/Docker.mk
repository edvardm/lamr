BUILDER ?= docker
BUILD_OPTS = build --tag $(IMAGE):$(IMAGE_TAG)

IMAGE ?= myapp
IMAGE_TAG ?= `git describe --tags --abbrev=0`
DOCKER_FILE ?= build/Dockerfile

REPO_URL =

.PHONY: build
build: ## Build production container image
	$(BUILDER) $(BUILD_OPTS) --tag $(IMAGE):latest -f $(DOCKER_FILE) .

.PHONY: build-dev
build-dev: ## Build development container image
	$(BUILDER) $(BUILD_OPTS) --tag $(IMAGE):dev -f $(DOCKER_FILE) .

publish-image:
	$(BUILDER) push $(REPO_URL)/$(IMAGE):$(IMAGE_TAG)
