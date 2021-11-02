.PHONY: mypy
mypy: ## Run static type checker
	@mypy --ignore-missing-imports \
		--disallow-incomplete-defs \
		--disallow-untyped-defs \
		--show-error-codes \
		--warn-unreachable \
		--warn-unused-ignores \
		*.py
