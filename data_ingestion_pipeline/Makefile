.PHONY: start
start:
	docker-compose -f docker-compose.yml up -d

.PHONY: stop
stop:
	docker-compose -f docker-compose.yml down

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