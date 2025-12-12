FROM certbot/certbot:latest

# HTTP-01 challenge mode
# Volumes will be mounted for:
# - /etc/letsencrypt (certificate storage)
# - /var/www/certbot (webroot for challenges)

ENTRYPOINT ["/bin/sh", "-c", "trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done"]
