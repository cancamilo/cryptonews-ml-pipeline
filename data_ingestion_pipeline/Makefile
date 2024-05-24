.PHONY: create-local-network
create-local-network:
	docker network create data_ingestion_pipeline_shared_network

.PHONY: start-mongodb
start-mongodb:
	docker-compose -f docker-compose.yml up -d

.PHONY: stop-mongodb
stop-mongodb:
	docker-compose -f docker-compose.yml down

.PHONY: crawler-local-build
crawler-local-build:
	@docker buildx build --platform linux/amd64 -t crawler -f crawler.dockerfile .

.PHONY: crawler-local-deploy
crawler-local-deploy: # Deploy lambda crawler custom docker image on local.
	docker run \
		-p 9000:8080 \
		--env-file .env.docker \
		--network data_ingestion_pipeline_shared_network \
		--platform linux/amd64 \
		crawler:latest

.PHONY: stop-crawler
stop-crawler: # Stop the crawler container
	@docker stop $$(docker ps -a -q --filter ancestor=crawler)

FORCE_BUILD=1

.PHONY: start
start: start-mongodb
ifeq ($(FORCE_BUILD),1)
	$(MAKE) crawler-local-build
endif
	$(MAKE) crawler-local-deploy

.PHONY: stop
stop-all: stop-mongodb
	@docker stop $$(docker ps -q)

MODE=daily

.PHONY: local-test
local-test: # Send test command on local to test  the lambda
	curl -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
	  	-d '{"mode": "$(MODE)"}'


invoke: # Invoke remote lambda from local
	aws lambda invoke \
		--function-name crawler \
		--cli-binary-format raw-in-base64-out \
		--payload '{"mode": "$(MODE)}]"}' \
		response.json