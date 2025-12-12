#!/bin/bash
# Certificate renewal script
# Can be run manually or via cron

set -e

echo "=== Renewing certificates ==="

docker compose run --rm certbot renew

echo "=== Reloading nginx ==="

docker compose exec nginx nginx -s reload

echo "=== Done ==="
