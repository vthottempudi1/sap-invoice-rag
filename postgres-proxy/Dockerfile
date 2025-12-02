FROM alpine:latest

RUN apk add --no-cache socat

COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 8080

CMD ["/start.sh"]
