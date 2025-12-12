# CF Demo Site - Implementation Plan

**Project:** probeopslab.com
**Status:** Planning Complete - Ready for Implementation
**Last Updated:** 2025-12-10

---

## Overview

Build a Docker-based demo lab website for Cloudflare tutorials, featuring redirect labs, geo-routing demos, and request debugging tools. The site will be ProbeOps-branded (minimal) and designed for screenshot-friendly video content.

---

## Phase 1: MVP Endpoints

| Endpoint | Type | Description |
|----------|------|-------------|
| `/` | Index | Lab home with links to all labs, timestamp, request ID |
| `/debug` | Debug | Sanitized request/geo headers display |
| `/robots.txt` | Static | `Disallow: /` for demo |
| `/redirect-lab` | Menu | Links to all redirect tests |
| `/r/301` | Redirect | 301 redirect to `/final` |
| `/r/302` | Redirect | 302 redirect to `/final` |
| `/r/307` | Redirect | 307 redirect to `/final` |
| `/r/308` | Redirect | 308 redirect to `/final` |
| `/final` | Landing | Final destination with full request context |
| `/geo-redirect` | Geo | Entry point for CF geo-based redirects |
| `/us` | Region | US region landing page |
| `/ca` | Region | Canada region landing page |
| `/fi` | Region | Finland region landing page |
| `/row` | Region | Rest of World landing page |
| `/host-lab` | Helper | Shows Host + scheme, links to www/apex variants |

**Planned (Week 2 - NOT in MVP):**
- `/pricing` - Region-based pricing demo
- `/cache-lab` - Cache behavior demos

---

## Phase 2: Project Structure

```
cf-demo-site/
├── docker-compose.yml          # Production config (default)
├── docker-compose.override.yml # Dev overrides (HTTP, hot-reload)
├── .env.example                 # Template for env vars
├── .env                         # Actual env vars (gitignored)
├── .gitignore
├── README.md
│
├── app/                         # FastAPI application
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                  # FastAPI app + routes
│   ├── templates/               # Jinja2 HTML templates
│   │   ├── base.html            # Base layout with branding
│   │   ├── index.html           # Lab index
│   │   ├── debug.html           # Debug page
│   │   ├── redirect_lab.html    # Redirect menu
│   │   ├── final.html           # Final landing
│   │   ├── geo_redirect.html    # Geo entry page
│   │   ├── region.html          # Region template (us/ca/fi/row)
│   │   └── host_lab.html        # Host/scheme helper
│   └── static/                  # CSS, optional assets
│       └── styles.css           # ProbeOps-branded styles
│
├── nginx/                       # NGINX configs
│   ├── nginx.conf               # Production config
│   ├── nginx.dev.conf           # Dev config (HTTP only)
│   └── snippets/
│       └── ssl.conf             # SSL settings
│
└── certbot/                     # TLS certificate management
    ├── Dockerfile               # Certbot with HTTP-01
    └── scripts/
        ├── init-cert.sh         # Initial cert issuance
        └── renew-cert.sh        # Renewal script
```

---

## Phase 3: Docker Services

### Production Stack (`docker-compose.yml`)

```yaml
services:
  app:
    # FastAPI with gunicorn
    # Internal only (not exposed)

  nginx:
    # Reverse proxy + TLS termination
    # Ports: 80, 443
    # Serves /.well-known/acme-challenge

  certbot:
    # Let's Encrypt HTTP-01 challenge
    # Shares volume with nginx
```

### Dev Stack (`docker-compose.override.yml`)

```yaml
services:
  app:
    # uvicorn --reload
    # Volume mount for hot reload
    # Port 8000 exposed directly (optional)

  nginx:
    # HTTP only (port 80)
    # Uses nginx.dev.conf
```

---

## Phase 4: Branding & Styling

### Design Tokens (from ProbeOps)

| Token | Value | Usage |
|-------|-------|-------|
| Primary Blue | `#1976d2` | Links, buttons, accents |
| Light Blue BG | `#e6f0fa` | Hover states, highlights |
| Dark Terminal | `#111827` | Code/debug output bg |
| Text Primary | `#374151` | Body text |
| Text Muted | `#6b7280` | Secondary text |
| Card Shadow | `0 4px 6px -1px rgba(0,0,0,0.1)` | Card elevation |
| Border Radius | `0.5rem` | Cards, buttons |
| Font Body | `Roboto, Inter, system-ui` | All text |
| Font Mono | `JetBrains Mono, monospace` | Code, debug |

### Page Layout

```
┌─────────────────────────────────────────┐
│  ProbeOps Demo Lab    [minimal header]  │
├─────────────────────────────────────────┤
│                                         │
│  [Big Label / Page Title]               │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │  Content Card                   │    │
│  │  - Clean, readable              │    │
│  │  - Screenshot-friendly          │    │
│  └─────────────────────────────────┘    │
│                                         │
├─────────────────────────────────────────┤
│  Demo site for tutorials only. ProbeOps │
└─────────────────────────────────────────┘
```

---

## Phase 5: NGINX Configuration

### Production Features
- TLS 1.2+ with modern ciphers
- HTTP → HTTPS redirect
- Proxy to FastAPI app
- Serve `/.well-known/acme-challenge` for Certbot
- Rate limiting (10 req/s per IP)
- Security headers (X-Frame-Options, etc.)

### Dev Features
- HTTP only (port 80)
- No TLS complexity
- Same proxy config to app
- No rate limiting

### www ↔ apex Handling
```nginx
# In server block - redirect www to apex
server {
    server_name www.probeopslab.com;
    return 301 https://probeopslab.com$request_uri;
}
```

---

## Phase 6: Implementation Order

### Step 1: Project Skeleton
- [ ] Create directory structure
- [ ] Set up `.gitignore`, `.env.example`
- [ ] Create base `docker-compose.yml`
- [ ] Create `docker-compose.override.yml` for dev

### Step 2: FastAPI App
- [ ] Create `Dockerfile` for app
- [ ] Set up FastAPI with Jinja2 templates
- [ ] Implement all MVP endpoints
- [ ] Create base template with branding
- [ ] Create individual page templates
- [ ] Add static CSS file

### Step 3: NGINX Configuration
- [ ] Create production `nginx.conf`
- [ ] Create dev `nginx.dev.conf`
- [ ] Configure upstream to app
- [ ] Set up ACME challenge location
- [ ] Add security headers
- [ ] Add rate limiting

### Step 4: Certbot Setup
- [ ] Create Certbot Dockerfile
- [ ] Create init script for first cert
- [ ] Create renewal script
- [ ] Set up shared volumes

### Step 5: Testing & Documentation
- [ ] Test dev workflow locally
- [ ] Document deployment steps in README
- [ ] Add troubleshooting section
- [ ] List planned features

---

## Phase 7: File Specifications

### Key Files to Create

| File | Lines (est.) | Priority |
|------|--------------|----------|
| `app/main.py` | ~150 | HIGH |
| `app/templates/base.html` | ~80 | HIGH |
| `app/templates/*.html` (8 files) | ~40 each | HIGH |
| `app/static/styles.css` | ~150 | HIGH |
| `app/Dockerfile` | ~20 | HIGH |
| `app/requirements.txt` | ~10 | HIGH |
| `nginx/nginx.conf` | ~100 | HIGH |
| `nginx/nginx.dev.conf` | ~50 | MEDIUM |
| `docker-compose.yml` | ~60 | HIGH |
| `docker-compose.override.yml` | ~30 | HIGH |
| `.env.example` | ~10 | HIGH |
| `README.md` | ~150 | MEDIUM |
| `certbot/scripts/*.sh` | ~30 each | MEDIUM |

---

## Phase 8: Security Checklist

- [ ] No login/auth required
- [ ] No file uploads
- [ ] No PII storage
- [ ] Header allowlist on `/debug` (no cookies/auth headers)
- [ ] Rate limiting in NGINX
- [ ] All secrets in `.env` (gitignored)
- [ ] Disclaimer footer on every page
- [ ] robots.txt disallows indexing

### Allowed Headers for `/debug`

```python
ALLOWED_HEADERS = [
    "host",
    "x-forwarded-for",
    "x-forwarded-proto",
    "x-real-ip",
    "cf-ray",
    "cf-ipcountry",
    "cf-ipcity",
    "cf-ipcontinent",
    "cf-region",
    "cf-connecting-ip",
    "user-agent",
    "accept-language",
    "accept-encoding",
]
```

---

## Approval Checklist

- [x] MVP endpoints defined
- [x] Project structure finalized
- [x] Docker workflow (dev + prod) confirmed
- [x] Branding approach confirmed
- [x] TLS approach (HTTP-01) confirmed
- [x] NGINX responsibilities clear
- [ ] **Ready to implement**

---

## Next Steps

Once approved, implementation will proceed in this order:

1. Create project skeleton with Docker configs
2. Build FastAPI app with all routes
3. Create HTML templates with styling
4. Configure NGINX (dev first, then prod)
5. Set up Certbot for production
6. Write README with full instructions
7. Test end-to-end locally

**Estimated files to create:** ~25
**Ready for live demo coding session:** Yes
