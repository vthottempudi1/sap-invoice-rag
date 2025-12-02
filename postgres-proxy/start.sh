#!/bin/bash
# SSH Tunnel Proxy for PostgreSQL
# This creates a simple TCP proxy to forward connections to PostgreSQL

PORT=${PORT:-8080}
TARGET_HOST=${TARGET_HOST:-postgres-e96ae2c4-8eb7-42bd-9ece-c5c50432af22.cqryblsdrbcs.us-east-1.rds.amazonaws.com}
TARGET_PORT=${TARGET_PORT:-6974}

echo "Starting TCP proxy on port $PORT"
echo "Forwarding to $TARGET_HOST:$TARGET_PORT"

socat TCP-LISTEN:$PORT,fork,reuseaddr TCP:$TARGET_HOST:$TARGET_PORT
