## ----------------------------------------------------------------------
## Commonly run commands for the Consensus-NLP/common repo.
## ----------------------------------------------------------------------

MAKEFLAGS += --no-builtin-rules
MAKEFLAGS += --no-builtin-variables

SHELL := /bin/bash
.SHELLFLAGS := --noprofile --norc -o pipefail -eu -c

PANTS := ./pants
PANTS_CHANGED_SINCE := ./pants --changed-since=origin/main --changed-dependees=transitive

DOCKER := DOCKER_BUILDKIT=1 docker
PWD := $(CURDIR)
WEB_FRONTEND := ./src/typescript/web
WEB_COMMON_FASTAPI_MOUNTABLE_DOCKERFILE := ./src/python/web/Dockerfile.local
LABELING := ./src/typescript/labeling
CHAT_GPT_PLUGIN := ./src/python/web/chat_gpt_plugin
DOCKER_COMPOSE_WEB := ./src/python/web/docker-compose.yml
DOCKER_COMPOSE_WEB_ENV := ./src/python/web/.env.local
DOCKER_COMPOSE_CHAT_GPT_PLUGIN := ./src/python/web/chat_gpt_plugin/docker-compose.yml
WEB_INIT_SCRIPT := $(PWD)/src/python/web/scripts/ingest_mock_data.py
WEB_STRIPE_INIT_SCRIPT := $(PWD)/src/python/web/scripts/populate_subscription_products_table.py
CHECK_PROD_SITEMAP_SCRIPT := ./src/python/web/scripts/check_prod_sitemap.py
PRETTIER := prettier --config .prettierrc.json

help:		## Show this help menu
	@sed -ne '/@sed/!s/## //p' $(MAKEFILE_LIST)

clean:	        ## Deletes pants cache directories
	rm -rf .pants.d \
		&& rm -rf .cache \
		&& rm -rf .pids

test:		## Run all python tests in the project
	$(PANTS_CHANGED_SINCE) test

test-fe:	## Run all frontend tests in the project
	yarn --cwd $(WEB_FRONTEND) test --coverage

integration-test:	## Run all frontend tests in the project
	yarn --cwd $(WEB_FRONTEND) cypress:spec

check:		## Runs python lint and type checking
	$(PANTS_CHANGED_SINCE) lint && $(PANTS_CHANGED_SINCE) check

check-fe:	## Runs frontend lint and type checking
	yarn --cwd $(WEB_FRONTEND) lint && \
		yarn --cwd $(WEB_FRONTEND) $(PRETTIER) --check . && \
		yarn --cwd $(WEB_FRONTEND) ts

check-labeling:	## Runs labeling lint and type checking
	yarn --cwd $(LABELING) lint && \
		yarn --cwd $(LABELING) $(PRETTIER) --check . && \
		yarn --cwd $(LABELING) ts

check-prod-sitemap:  ## Runs python script to check existence of production sitemap
	$(PANTS) run $(CHECK_PROD_SITEMAP_SCRIPT)

fmt:		## Auto-formats the code
	$(PANTS_CHANGED_SINCE) fmt && $(PANTS_CHANGED_SINCE) fix

fmt-fe:		## Auto-formats the frontend code
	yarn --cwd $(WEB_FRONTEND) $(PRETTIER) --write .

fmt-labeling:   ## Auto-formats the labeling frontend code
	yarn --cwd $(LABELING) $(PRETTIER) --write .

package:	## Build all packages in the project
	$(PANTS) package ::

build_fastapi_mountable_local_dockerfile := $(DOCKER) build -t common_fastapi_docker -f $(WEB_COMMON_FASTAPI_MOUNTABLE_DOCKERFILE) .
build_web_fe := $(DOCKER) build -t frontend_docker --target base -f $(WEB_FRONTEND)/Dockerfile .
build_web := $(build_fastapi_mountable_local_dockerfile) && $(build_web_fe)
build_labeling := $(DOCKER) build -t labeling_docker --target base -f $(LABELING)/Dockerfile .

web-build:      ## Build docker containers for web app
	$(build_web)

web:            ## Starts a local instance of the web app backend
	$(build_web) && \
		docker-compose \
		  --file $(DOCKER_COMPOSE_WEB) \
		  --env-file $(DOCKER_COMPOSE_WEB_ENV) \
		  up --abort-on-container-exit

web-init:	## Populates locally running web app backend with mock data
		## This must be called while `make web` is running
		## WARNING: This is destructive and deletes existing mock data
	$(DOCKER) run -i \
		-v $(PWD)/src:/shared/common/src \
		-v $(PWD)/.git:/shared/common/.git \
		-v $(WEB_INIT_SCRIPT):/shared/common/main.py \
		-v web_shared_common_data:/shared/common/data \
		-w /shared/common \
		--net="host" \
		--rm common_fastapi_docker:latest \
		'python main.py'

web-stripe-init:	## Populates locally running web app backend with stripe data
			## This must be called while `make web` is running
	$(DOCKER) run -i \
		-v $(PWD)/src:/shared/common/src \
		-v $(PWD)/.git:/shared/common/.git \
		-v $(WEB_STRIPE_INIT_SCRIPT):/shared/common/main.py \
		-v web_shared_common_data:/shared/common/data \
		-w /shared/common \
		--net="host" \
		--rm common_fastapi_docker:latest \
		'python main.py'

web-fe:         ## Starts a local instance of the web app frontend
	$(build_web_fe) && \
		docker run \
		--rm \
		--name="frontend" \
		-p 3000:3000 \
		-v $(PWD)/src/typescript/web/src:/fe-app/src \
		frontend_docker:latest yarn dev

labeling:       ## Starts a local instance of the labeling app
	$(build_labeling) && \
		docker run \
		--rm \
		--name="labeling" \
		-p 3000:3000 \
		-v $(PWD)/src/typescript/labeling/src:/fe-app/src \
		labeling_docker:latest yarn dev

chat-gpt-plugin:            ## Starts a local instance of the chat gpt plugin
	$(build_fastapi_mountable_local_dockerfile) && \
		docker-compose \
		  --file $(DOCKER_COMPOSE_CHAT_GPT_PLUGIN) \
		  --env-file $(DOCKER_COMPOSE_WEB_ENV) \
		  up --abort-on-container-exit
