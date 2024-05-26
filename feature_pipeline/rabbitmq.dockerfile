FROM rabbitmq:3-management-alpine

ADD init.sh /init.sh
RUN chmod +x /init.sh

CMD ["/init.sh"]