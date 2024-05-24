# AWS_CURRENT_REGION_ID := $(shell aws configure get region)
# AWS_CURRENT_ACCOUNT_ID := $(shell aws sts get-caller-identity --query "Account" --output text)
help:
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

.PHONY: create-local-network
create-local-network:
	docker network create data_ingestion_pipeline_shared_network

.PHONY: start-mongodb
start-mongodb:
	docker-compose -f data_ingestion_pipeline/docker-compose.yml up -d

.PHONY: stop-mongodb
stop-mongodb:
	docker-compose -f data_ingestion_pipeline/docker-compose.yml down

.PHONY: crawler-local-build
crawler-local-build:
	@docker buildx build --platform linux/amd64 -t crawler -f data_ingestion_pipeline/crawler.dockerfile .

.PHONY: crawler-local-deploy
crawler-local-deploy: # Deploy lambda crawler custom docker image on local.
	docker run \
		-p 9000:8080 \
		--env-file .env.docker \
		--network data_ingestion_pipeline_shared_network \
		--platform linux/amd64 \
		crawler:latest

.PHONY: cdc-local-build
cdc-local-build:
	docker buildx build --platform linux/amd64 -t cdc -f mongo_sync_pipeline/cdc.dockerfile .

.PHONY: cdc-local-deploy
cdc-local-deploy:
	docker run \
		-p 7000:8000 \
		--env-file .env.docker \
		--network data_ingestion_pipeline_shared_network \
		--platform linux/amd64 \
		cdc:latest

.PHONY: stop-crawler
stop-crawler: # Stop the crawler container
	@docker stop $$(docker ps -a -q --filter ancestor=crawler)

.PHONY: stop-cdc
stop-cdc: # Stop the crawler container
	@docker stop $$(docker ps -a -q --filter ancestor=cdc)

FORCE_BUILD=1

.PHONY: start-services
start-services: start-mongodb
ifeq ($(FORCE_BUILD),1)
	$(MAKE) crawler-local-build cdc-local-build
endif
	$(MAKE) crawler-local-deploy cdc-local-deploy

.PHONY: stop-all
stop-all: stop-mongodb
	@docker stop $$(docker ps -q)

.PHONY: remove-images
remove-images: # Remove all Docker images
	@docker rmi -f $$(docker images -q)

local-test: # Send test command on local to test  the lambda
	curl -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
	  	-d '{"mode": "backfill"}'

invoke: # Invoke remote lambda from local
	aws lambda invoke \
		--function-name crawler \
		--cli-binary-format raw-in-base64-out \
		--payload '{"mode": "daily"}' \
		response.json

push: # Build & push image to docker ECR (e.g make push IMAGE_TAG=latest)
	echo "Logging into AWS ECR..."
	aws ecr get-login-password --region $(AWS_CURRENT_REGION_ID) | docker login --username AWS --password-stdin $(AWS_CURRENT_ACCOUNT_ID).dkr.ecr.$(AWS_CURRENT_REGION_ID).amazonaws.com
	echo "Build & Push Docker image..."
	docker buildx build --platform linux/amd64 -t $(AWS_CURRENT_ACCOUNT_ID).dkr.ecr.$(AWS_CURRENT_REGION_ID).amazonaws.com/crawler:$(IMAGE_TAG) .
	echo "Push completed successfully."

clean: # Cleanup files generated during sam building.
	@echo "Cleaning old files..."
	rm -rf /.pytest_cache
	rm -rf /__pycache
	rm -rf */.pyc
	rm -rf .mypy_cache
	@echo "Done."
