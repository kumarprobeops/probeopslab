# ProbeOps Lab

A self-hosted test lab for debugging redirects, caching, timeouts, and HTTP headers. Like httpbin, but focused on CDN/edge behavior.

## Quick Start

**Option 1: Use the hosted instance** (zero setup)

```bash
curl -s https://probeopslab.com/debug.json | jq '{ip: .client_ip, country: .country}'
```

**Option 2: Self-host** (for internal networks, CI/CD, or reproducing production behavior)

```bash
git clone https://github.com/kumarprobeops/probeopslab.git
cd probeopslab
docker compose up -d
```

Open http://localhost:8000 - done.

## Why Self-Host?

- **Test against your own infrastructure** - Debug issues in internal networks, staging environments, or behind corporate firewalls
- **No external dependencies** - Run tests in CI/CD pipelines without hitting external services
- **Reproduce production behavior** - Run it behind your own LB/WAF/CDN to test real header/redirect/cache behavior
- **Full control** - No rate limits, no third-party dependencies, no surprises

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

## Architecture

| Mode | Access | Use Case |
|------|--------|----------|
| Development | `localhost:8000` (app direct) | Local testing, hot-reload |
| Production | `:80/:443` (nginx → app) | SSL termination, rate limiting |

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

Once HTTP is working, use the init script:

```bash
./certbot/scripts/init-cert.sh
```

Or manually:

```bash
mkdir -p certbot/www
docker compose -f docker-compose.yml up -d nginx app
docker compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email your-email@example.com \
    --agree-tos \
    --no-eff-email \
    -d yourdomain.com \
    -d www.yourdomain.com
docker compose exec nginx nginx -s reload
```

### Step 4: Verify HTTPS

```bash
curl -I https://yourdomain.com/debug
```

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
nano cloudflare/fullchain.pem   # Paste certificate
nano cloudflare/privkey.pem     # Paste private key
```

4. The `cloudflare/` directory is already mounted into nginx at `/etc/nginx/cloudflare/` (see docker-compose.yml)

5. Update `nginx/snippets/ssl.conf` to use Cloudflare certs:

```nginx
ssl_certificate /etc/nginx/cloudflare/fullchain.pem;
ssl_certificate_key /etc/nginx/cloudflare/privkey.pem;
```

6. In Cloudflare dashboard: SSL/TLS > Overview > Set to "Full (strict)"
7. Enable orange cloud (proxy) on DNS records

### Cloudflare Headers

When proxied through Cloudflare, your `/debug` endpoint will show additional headers:

- `cf-ray` - Unique request ID
- `cf-ipcountry` - Visitor's country code
- `cf-connecting-ip` - Visitor's real IP
- `cf-ipcity`, `cf-region` - Geo data (Business/Enterprise plans)

## Security & Privacy

This is a stateless debugging tool with minimal attack surface:

- **No cookies or sessions** - Each request is independent
- **No data storage** - Nothing is persisted, no database
- **Header allowlist** - `/debug` only exposes safe headers (host, user-agent, geo headers). Auth headers, cookies, and tokens are never shown.
- **Rate limiting** - Default 10 req/s per IP (burst 20) in production nginx config
- **No tracking** - No analytics, no third-party scripts

Safe to run in corporate networks.

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

## Contributing

PRs welcome. Keep it simple - this is a utility, not a framework.

## License

MIT
