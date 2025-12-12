# ProbeOps Lab

A self-hosted test lab for debugging CDN behavior, redirects, caching, and geo-routing. Deploy it in your infrastructure and get predictable, controllable endpoints for testing.

## Why Self-Host?

- **Test against your own infrastructure** - Debug issues in internal networks, staging environments, or behind corporate firewalls
- **No external dependencies** - Run tests in CI/CD pipelines without hitting external services
- **Customize for your needs** - Add endpoints specific to your testing scenarios
- **Full control** - No rate limits, no third-party dependencies, no surprises

## Quick Start (Local Development)

```bash
git clone https://github.com/kumarprobeops/probeopslab.git
cd probeopslab
docker compose up -d
```

Open http://localhost:8000 - you're running.

The dev setup runs HTTP-only with hot-reload enabled. Edit files in `app/` and changes apply immediately.

## Endpoints

| Path | Description |
|------|-------------|
| `/debug` | Your IP, geo headers, request info |
| `/debug.json` | Same as above, JSON format for scripts |
| `/r/301`, `/r/302`, `/r/307`, `/r/308` | Redirect with specific status code |
| `/status/{code}` | Return specific HTTP status (200, 404, 500, etc.) |
| `/delay/{ms}` | Respond after N milliseconds |
| `/size/{bytes}` | Return N-byte response body |
| `/cache/*` | Various Cache-Control header configurations |
| `/use-cases` | Real-world troubleshooting scenarios |

## Production Deployment

### Prerequisites

- A server with Docker and Docker Compose installed
- A domain name pointing to your server's IP
- Ports 80 and 443 open

### Step 1: Clone and Configure

```bash
git clone https://github.com/kumarprobeops/probeopslab.git
cd probeopslab
cp .env.example .env
```

Edit `.env`:
```bash
DOMAIN=yourdomain.com
LE_EMAIL=your-email@example.com
```

### Step 2: Initial Setup (HTTP only)

First, start with the dev config to verify everything works:

```bash
docker compose up -d
curl http://yourdomain.com/debug
```

### Step 3: Get SSL Certificate (Let's Encrypt)

Once HTTP is working, issue a certificate:

```bash
# Create certificate directory
mkdir -p certbot/www

# Start production stack (will fail SSL initially, that's expected)
docker compose -f docker-compose.yml up -d nginx app

# Issue certificate
docker compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email your-email@example.com \
    --agree-tos \
    --no-eff-email \
    -d yourdomain.com \
    -d www.yourdomain.com

# Reload nginx to pick up the new certificate
docker compose exec nginx nginx -s reload
```

### Step 4: Verify HTTPS

```bash
curl -I https://yourdomain.com/debug
```

You should see a 200 response with valid SSL.

### Certificate Auto-Renewal

The nginx container automatically reloads every 6 hours. Set up a cron job for renewal:

```bash
# Add to crontab (crontab -e)
0 0 * * * cd /path/to/probeopslab && docker compose run --rm certbot renew --quiet
```

## Deploying Behind Cloudflare

If you're putting this behind Cloudflare (recommended for production), there are two SSL options:

### Option A: Let's Encrypt + Cloudflare (Full Strict)

1. Follow the Let's Encrypt setup above
2. In Cloudflare dashboard: SSL/TLS > Overview > Set to "Full (strict)"
3. Enable the orange cloud (proxy) on your DNS records

### Option B: Cloudflare Origin Certificate (Simpler)

Cloudflare Origin Certificates are free, valid for 15 years, and simpler to manage:

1. In Cloudflare dashboard: SSL/TLS > Origin Server > Create Certificate
2. Copy the certificate and private key
3. Save them to your server:

```bash
mkdir -p cloudflare
# Paste certificate content
nano cloudflare/fullchain.pem
# Paste private key content
nano cloudflare/privkey.pem
```

4. Update `nginx/snippets/ssl.conf` to use Cloudflare certs:

```nginx
ssl_certificate /etc/nginx/cloudflare/fullchain.pem;
ssl_certificate_key /etc/nginx/cloudflare/privkey.pem;
```

5. In Cloudflare dashboard: SSL/TLS > Overview > Set to "Full (strict)"
6. Enable orange cloud (proxy) on DNS records

### Cloudflare Headers

When proxied through Cloudflare, your `/debug` endpoint will show additional headers:

- `cf-ray` - Unique request ID
- `cf-ipcountry` - Visitor's country code
- `cf-connecting-ip` - Visitor's real IP
- `cf-ipcity`, `cf-region` - Geo data (Business/Enterprise plans)

These are useful for testing geo-routing rules.

## Project Structure

```
probeopslab/
├── app/
│   ├── main.py              # FastAPI routes
│   ├── templates/           # Jinja2 HTML templates
│   ├── static/              # CSS, assets
│   ├── Dockerfile
│   └── requirements.txt
├── nginx/
│   ├── nginx.conf.template  # Production config (HTTPS)
│   ├── nginx.dev.conf       # Dev config (HTTP only)
│   └── snippets/
│       └── ssl.conf         # SSL certificate paths
├── certbot/
│   ├── Dockerfile
│   └── scripts/
│       ├── init-cert.sh     # First-time cert issuance
│       └── renew-cert.sh    # Renewal script
├── cloudflare/              # Cloudflare Origin certs (if using)
├── docker-compose.yml       # Production config
├── docker-compose.override.yml  # Dev overrides (auto-loaded)
└── .env.example             # Environment template
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DOMAIN` | Your domain name | `localhost` |
| `LE_EMAIL` | Email for Let's Encrypt notifications | required |

### NGINX Settings

The production config includes:
- Rate limiting: 10 req/s per IP (burst 20)
- Gzip compression
- Security headers (X-Frame-Options, X-Content-Type-Options, etc.)
- HTTP/2 enabled
- www to apex redirect

Adjust in `nginx/nginx.conf.template` as needed.

## Common Operations

```bash
# Start development (HTTP, hot-reload)
docker compose up -d

# View logs
docker compose logs -f app

# Rebuild after code changes
docker compose up -d --build app

# Start production (HTTPS)
docker compose -f docker-compose.yml up -d

# Renew SSL certificate
docker compose run --rm certbot renew
docker compose exec nginx nginx -s reload

# Check nginx config
docker compose exec nginx nginx -t
```

## Troubleshooting

**Certificate issuance fails**
- Ensure port 80 is open and reachable
- Check DNS is pointing to your server
- Verify `.well-known/acme-challenge/` is accessible

**502 Bad Gateway**
- Check if app container is running: `docker compose ps`
- Check app logs: `docker compose logs app`

**Cloudflare shows 525/526 errors**
- SSL mode should be "Full (strict)" not "Flexible"
- Certificate must be valid (Let's Encrypt or Origin CA)

## Public Instance

Don't want to self-host? We run a public instance at **https://probeopslab.com** for quick tests.

## Contributing

PRs welcome. Keep it simple - this is a utility, not a framework.

## License

MIT
