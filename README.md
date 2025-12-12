# CF Demo Labs

Cloudflare demo lab website for tutorials at `probeopslab.com`.

Features redirect labs, geo-routing demos, and request debugging tools.

## Quick Start (Development)

```bash
# Clone and navigate to project
cd cf-demo-site

# Start development environment
docker compose up -d

# View logs
docker compose logs -f app

# Access the site
open http://localhost
```

The development setup runs HTTP only (no TLS) with hot-reload enabled.

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `/` | Lab index with links to all labs |
| `/debug` | Request headers and geo data display |
| `/redirect-lab` | Redirect test menu |
| `/r/301`, `/r/302`, `/r/307`, `/r/308` | Redirect endpoints |
| `/final` | Redirect destination page |
| `/geo-redirect` | Geo routing entry point |
| `/us`, `/ca`, `/fi`, `/row` | Region landing pages |
| `/host-lab` | Host/scheme testing |

## Production Deployment

### Prerequisites

- VPS with Docker and Docker Compose installed
- Domain pointing to server IP (DNS A record)
- Cloudflare account (optional, for proxy features)

### Setup

1. **Clone the repository:**
   ```bash
   git clone <repo-url> cf-demo-site
   cd cf-demo-site
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

3. **Start services (without TLS first):**
   ```bash
   # Start app and nginx with HTTP only
   docker compose up -d app nginx
   ```

4. **Issue TLS certificate:**
   ```bash
   # Create webroot directory
   mkdir -p certbot/www certbot/conf

   # Issue certificate
   docker compose run --rm certbot certonly \
       --webroot \
       --webroot-path=/var/www/certbot \
       --email your-email@example.com \
       --agree-tos \
       --no-eff-email \
       -d probeopslab.com \
       -d www.probeopslab.com
   ```

5. **Switch to production NGINX config:**
   ```bash
   # Remove override file to use production config
   rm docker-compose.override.yml

   # Restart nginx with TLS
   docker compose up -d
   ```

6. **Verify:**
   ```bash
   curl -I https://probeopslab.com
   ```

### Certificate Renewal

Certificates auto-renew via the certbot container. To manually renew:

```bash
docker compose run --rm certbot renew
docker compose exec nginx nginx -s reload
```

### Cloudflare Integration

After TLS is working:

1. Set DNS record to **Proxied** (orange cloud)
2. Configure SSL/TLS mode to **Full (strict)**
3. Create Redirect Rules for geo-based routing:

   ```
   # Example: Redirect CA visitors
   Expression: (http.request.uri.path eq "/geo-redirect" and ip.geoip.country eq "CA")
   Action: Redirect to /ca (302)
   ```

## Project Structure

```
cf-demo-site/
├── app/                    # FastAPI application
│   ├── main.py            # Routes and logic
│   ├── templates/         # Jinja2 HTML templates
│   └── static/            # CSS and assets
├── nginx/                  # NGINX configuration
│   ├── nginx.conf         # Production config
│   ├── nginx.dev.conf     # Development config
│   └── snippets/          # SSL settings
├── certbot/               # Let's Encrypt
│   └── scripts/           # Cert management scripts
├── docker-compose.yml     # Production compose
└── docker-compose.override.yml  # Dev overrides
```

## Troubleshooting

### Certificate Issues

If certificates fail to issue:

```bash
# Check ACME challenge is accessible
curl http://probeopslab.com/.well-known/acme-challenge/test

# View certbot logs
docker compose logs certbot
```

### App Not Responding

```bash
# Check app health
docker compose exec app python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/').status)"

# View app logs
docker compose logs -f app
```

### NGINX Config Test

```bash
docker compose exec nginx nginx -t
```

## Development

### Hot Reload

The dev setup mounts the `app/` directory, so changes to Python files and templates are reflected immediately.

### Adding New Endpoints

1. Add route in `app/main.py`
2. Create template in `app/templates/`
3. Refresh browser

## License

Demo site for ProbeOps tutorials.
