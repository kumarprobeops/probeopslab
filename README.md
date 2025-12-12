# ProbeOps Lab

A public reference edge for testing CDN behavior, redirects, caching, and geo-routing.

**Live:** https://probeopslab.com

## The Problem

You're debugging why:
- Your CDN isn't caching what it should
- Your 301 redirects are actually 302s (RIP SEO)
- Your geo-routing sends Canadians to the US site
- Your load balancer times out before the backend responds
- Your VPN is leaking your real IP

You need a stable, predictable endpoint that doesn't change. Not your staging server that breaks every sprint.

## What This Is

A minimal, stateless test lab running behind Cloudflare. No cookies, no auth, no tracking. Just predictable responses you can curl against.

```bash
# What's my IP and country?
curl -s https://probeopslab.com/debug.json | jq '{ip: .client_ip, country: .country}'

# Is this a 301 or 302?
curl -sI https://probeopslab.com/r/301 | grep HTTP

# Simulate a slow backend
curl -w "Time: %{time_total}s\n" https://probeopslab.com/delay/3000

# Get a 503 to test error handling
curl -sI https://probeopslab.com/status/503
```

## Endpoints

| Path | What it does |
|------|--------------|
| `/debug` | Shows your IP, geo, headers |
| `/debug.json` | Same, but JSON for scripts |
| `/r/301`, `/r/302`, `/r/307`, `/r/308` | Redirect with specific status code |
| `/cache/*` | Various Cache-Control headers |
| `/delay/{ms}` | Respond after N milliseconds |
| `/status/{code}` | Return specific HTTP status |
| `/size/{bytes}` | Return N-byte response |

Full list at https://probeopslab.com/use-cases

## Run Your Own

```bash
git clone https://github.com/kumarprobeops/probeopslab.git
cd probeopslab
cp .env.example .env
# Edit .env with your domain
docker compose up -d
```

Needs SSL certs in `cloudflare/` directory (Cloudflare Origin CA or Let's Encrypt).

## Stack

- FastAPI + Jinja2
- NGINX
- Docker Compose
- Cloudflare (optional but recommended)

## Contributing

PRs welcome. Keep it simple. This is a utility, not a framework.

## License

MIT
