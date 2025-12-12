#!/bin/bash
# Initial certificate issuance script
# Run this ONCE on first deployment

set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | xargs)
fi

DOMAIN=${DOMAIN:-probeopslab.com}
EMAIL=${LE_EMAIL:-admin@probeops.com}

echo "=== Issuing certificate for $DOMAIN ==="

# Create webroot directory if it doesn't exist
mkdir -p ./certbot/www

# Issue certificate using HTTP-01 challenge
docker compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    -d "$DOMAIN" \
    -d "www.$DOMAIN"

echo "=== Certificate issued successfully ==="
echo "Reloading nginx..."

docker compose exec nginx nginx -s reload

echo "=== Done ==="
