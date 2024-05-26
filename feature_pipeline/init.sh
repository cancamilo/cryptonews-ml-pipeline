#!/bin/sh
export RABBITMQ_PID_FILE=/var/lib/rabbitmq/mnesia/rabbit@localhost.pid

rabbitmq-server -detached
rabbitmqctl wait --timeout 60 $RABBITMQ_PID_FILE
rabbitmqctl add_user test test
rabbitmqctl set_user_tags test administrator
rabbitmqctl set_permissions -p / test ".*" ".*" ".*"
rabbitmqctl stop
sleep 5
rabbitmq-server