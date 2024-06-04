# AWS_CURRENT_REGION_ID := $(shell aws configure get region)
# AWS_CURRENT_ACCOUNT_ID := $(shell aws sts get-caller-identity --query "Account" --output text)
help:
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

.PHONY: start
start:
	docker-compose -f docker-compose.yml up -d --build

.PHONY: stop
stop:
	docker-compose -f docker-compose.yml down

scrolls=20
k_channel=20 

.PHONY: run_backfill
run_backfill:
	@poetry -C data_ingestion_pipeline run python data_ingestion_pipeline/backfill.py --scrolls=$(scrolls) --k_channel=$(k_channel)

.PHONY: crawler-docker-build
crawler-docker-build:
	@docker buildx build --platform linux/amd64 -t crawler -f data_ingestion_pipeline/crawler.dockerfile data_ingestion_pipeline

.PHONY: crawler-docker-run
crawler-docker-run:
	@docker run --name crawler-lambda -p 9000:8080 -d --env-file data_ingestion_pipeline/.env.docker --network text-fetch-etl_default --platform linux/amd64 crawler:latest

.PHONY: cdc-docker-build
cdc-docker-build:
	docker buildx build --platform linux/amd64 -t cdc -f mongodb_sync/cdc.dockerfile mongodb_sync

.PHONY: cdc-docker-run
cdc-docker-run:
	docker run \
		--name cdc-service \
		-p 7000:8000 \
		-d \
		--env-file .env.docker \
		--network text-fetch-etl_default \
		--platform linux/amd64 \
		cdc:latest

.PHONY: streamer-docker-build
streamer-docker-build:
	docker buildx build --platform linux/amd64 -t stream_processor -f feature_pipeline/stream_processor.dockerfile feature_pipeline

.PHONY: streamer-docker-run
streamer-docker-run:
	docker run \
		--name stream-processor \
		-d \
		--network text-fetch-etl_default \
		--platform linux/amd64 \
		stream_processor:latest
	

.PHONY: stop-crawler
stop-crawler: # Stop the crawler container
	@docker stop $$(docker ps -a -q --filter ancestor=crawler)

.PHONY: stop-cdc
stop-cdc: # Stop the crawler container
	@docker stop $$(docker ps -a -q --filter ancestor=cdc)

.PHONY: stop-streamer
streamer-cdc: # Stop the crawler container
	@docker stop $$(docker ps -a -q --filter ancestor=streamer)

.PHONY: stop-services
stop-services:
	@docker stop $$(docker ps -q -a) & docker rm -f $$(docker ps -a -q)

.PHONY: remove-images
remove-images: # Remove all Docker images
	@docker rmi -f $$(docker images -q)

test-daily: # Send test command on local to test  the lambda
	curl -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
	  	-d '{"mode": "backfill"}'

test-backfill: # Send test command on local to test  the lambda
	curl -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
	  	-d '{"mode": "backfill", "scrolls": 40}'
