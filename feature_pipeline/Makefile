help:
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

.PHONY: start
start: # Build services.
	docker-compose -f docker-compose.yml up --build -d

.PHONY: stop
stop: # Stop mongodb, mq and qdrant.
	docker-compose -f docker-compose.yml down

local-bytewax: # Run bytewax pipeline
	RUST_BACKTRACE=full poetry run python -m bytewax.run data_flow/bytewax_pipeline

build-docker-flow:
	@docker buildx build --platform linux/amd64 -t stream_processor -f stream_processor.dockerfile .

start-docker-flow:
	@docker run \
		--name stream-processor \
		-p 9000:8080 \
		--network feature_pipeline_default \
		--platform linux/amd64 \
		stream_processor:latest