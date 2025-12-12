#!/bin/sh
set -e

# Default values
DOMAIN=${DOMAIN:-localhost}

echo "Configuring nginx for domain: $DOMAIN"

# Replace placeholders in nginx config template
envsubst '${DOMAIN}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

echo "nginx configuration generated successfully"

# Execute the original nginx command
exec "$@"
