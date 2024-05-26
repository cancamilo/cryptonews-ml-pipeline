#!/bin/bash

# Wait for mq to be ready
until nc -z mq 5672; do
    echo "$(date) - waiting for mq service..."
    sleep 10
done

# Start the stream_processor service
exec "$@"