K8S_BUILD = kustomize build --enable-alpha-plugins
SKAFFOLD_FLAGS ?= --force --port-forward
OVERLAY ?= k8s/overlays/production

PHONY: k8s-dev
k8s-dev: ## Run k8s in dev mode
	skaffold dev $(SKAFFOLD_FLAGS)

k8s-deploy: ## Deploy to k8s cluster
	skaffold build --tag $(TAG) && skaffold deploy --force $(TAG)

k8s-lint: ## Validate k8s configs
	$(K8S_BUILD) $(OVERLAY) | kubeval
