# ProbeOps Lab

Cloudflare demo lab for tutorials - redirect testing, geo-routing, and request debugging.

## Features

- **Redirect Labs** - Test 301, 302, 307, 308 redirects
- **Geo-Routing** - Cloudflare geo-based redirect demos
- **Request Debugger** - View headers, IP, and geo data
- **Host Lab** - Test www/apex and HTTP/HTTPS behavior

## Quick Start

### 1. Clone and Configure

```bash
git clone https://github.com/kumarprobeops/probeopslab.git
cd probeopslab

# Create your configuration
cp .env.example .env
```

Edit `.env` with your domain:

```env
DOMAIN=yourdomain.com
LE_EMAIL=your-email@example.com
```

### 2. Add SSL Certificates

Place your SSL certificates in the `cloudflare/` directory:

```bash
mkdir -p cloudflare
# Add your certificates:
# cloudflare/fullchain.pem
# cloudflare/privkey.pem
```

**Options for certificates:**
- **Cloudflare Origin CA** - Free certificates for Cloudflare-proxied domains
- **Let's Encrypt** - Use the included certbot container
- **Self-signed** - For local testing only

### 3. Start Services

```bash
docker compose up -d
```

### 4. Verify

```bash
curl -I https://yourdomain.com
```

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

## Using Let's Encrypt

If you prefer Let's Encrypt over Cloudflare Origin CA:

```bash
# Start services without SSL first (modify nginx config)
# Then issue certificate:
docker compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $LE_EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN

# Restart nginx
docker compose restart nginx
```

## Cloudflare Integration

For full Cloudflare features:

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
probeopslab/
├── app/                    # FastAPI application
│   ├── main.py             # Routes and logic
│   ├── templates/          # Jinja2 HTML templates
│   └── static/             # CSS and assets
├── nginx/                  # NGINX configuration
│   ├── nginx.conf.template # Config template (uses $DOMAIN)
│   ├── docker-entrypoint.sh # Generates config from template
│   └── snippets/           # SSL settings
├── certbot/                # Let's Encrypt automation
├── cloudflare/             # SSL certificates (gitignored)
├── docker-compose.yml      # Main compose file
└── .env.example            # Configuration template
```

## Development

For local development without SSL:

```bash
# Use the dev nginx config
cp nginx/nginx.dev.conf nginx/nginx.conf.template

# Start services
docker compose up -d

# Access at http://localhost
```

## Troubleshooting

### NGINX Config Test

```bash
docker compose exec nginx nginx -t
```

### View Logs

```bash
docker compose logs -f app
docker compose logs -f nginx
```

### App Health Check

```bash
docker compose exec app python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/').status)"
```

## License

MIT License - See LICENSE file for details.
