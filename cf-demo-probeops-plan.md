# probeopslab.com — Cloudflare Geo / Redirect Labs (Plan)

Last updated: 2025-12-10 (IST)

## 1) Purpose

Build a **stable demo “lab” website** at **`probeopslab.com`** that we can use to:

- publish *mile-deep* Cloudflare tutorials (Redirect Rules, Transform Rules, Headers, Geo, SSL/TLS)
- **reproduce predictable behaviors** (redirect chains, geo routing, header transforms)
- **verify from real geographies** using **ProbeOps Horizon (multi-geo browser)** + **ProbeOps Terminal (curl/ping/traceroute from region)**

This is not just for videos—keep it online so users can test and we can reuse the same scenarios forever.

---

## 2) High-level architecture

- **Domain:** `probeopslab.com`
- **Hosting:** separate small VPS (or separate Docker host) so experiments never affect production
- **Runtime:** Docker Compose
- **Reverse proxy:** NGINX
- **TLS:** Let’s Encrypt via Certbot (recommended DNS-01 so it works even when Cloudflare proxy is ON)
- **App:** simple web app exposing lab endpoints (FastAPI recommended for speed + clarity)

```
Internet
  |
Cloudflare (proxy + rules)
  |
NGINX (TLS termination)
  |
Demo App container (FastAPI)
```

---

## 3) DNS record

Create either:

- **CNAME**: `probeopslab.com` → demo server hostname (recommended if you have a stable hostname), OR
- **A record**: `probeopslab.com` → demo server public IP

Cloudflare proxy status:
- For real Cloudflare testing, set it to **Proxied (orange cloud)** after certificate is ready.
- With DNS-01 issuance, it can stay proxied during issuance/renewal.

---

## 4) Lab content (MVP endpoints)

Design principles:
- Every page must be **screenshot-friendly** (big labels, minimal clutter).
- Every lab page should show: **Scenario ID**, **Expected behavior**, **What to test with ProbeOps**.
- Avoid collecting personal data. Sanitize request headers displayed.

### 4.1 Core pages

1. **`/`** — Lab index  
   - links to all labs  
   - short “what this site is” disclaimer  
   - shows current timestamp + request id  

2. **`/debug`** — Request & geo debug (read-only)  
   - Show:
     - host, scheme, path, query  
     - Cloudflare request id headers if present (e.g., `CF-Ray`)  
     - key geo headers if present (e.g., country / region / city)  
     - user-agent (truncated), accept-language  
   - Display a **sanitized** header table (allowlist only)

3. **`/robots.txt`**  
   - Start with `Disallow: /` (demo-only) until we decide to index  
   - Later we can allow indexing if we want the lab to rank

### 4.2 Redirect labs (vendor-agnostic behaviors)

4. **`/redirect-lab`** — Redirect menu  
   - Links that trigger standard redirect patterns:
     - `/r/301` → 301 to `/final`  
     - `/r/302` → 302 to `/final`  
     - `/r/307` → 307 to `/final`  
     - `/r/308` → 308 to `/final`  
   - “www ↔ apex” test link (depends on how we configure)  
   - “http ↔ https” test link (mostly via NGINX + Cloudflare SSL mode)

5. **`/final`**  
   - big “FINAL PAGE” label  
   - prints the *full request context* (sanitized)

### 4.3 Geo routing lab (Cloudflare-focused)

6. **`/geo-redirect`**  
   - This endpoint is designed to be the **target** of Cloudflare Redirect Rules:
     - Example behavior we want to demonstrate: if visitor is CA → `/ca`, FI → `/fi`, default → `/row`
   - Page shows:
     - what geo value Cloudflare detected (from headers)
     - what Cloudflare rule is expected to fire (we’ll document rule examples)

7. Region pages (big labels):  
   - **`/us`**, **`/ca`**, **`/fi`**, **`/row`**  
   - Each prints a large region label + debug info  

---

## 5) Nice-to-have (Week 2)

8. **`/pricing`** — region pricing demo  
   - Show currency/tax banner based on geo header  
   - Great for Horizon “Canada vs Helsinki” visuals  

9. **`/cache-lab`**  
   - endpoints demonstrating how caching can accidentally serve wrong region  
   - optional headers to show cache status  

---

## 6) NGINX + Certbot plan (Docker)

### Recommended TLS approach: DNS-01 (Cloudflare API)
Why:
- Works even when Cloudflare proxy is ON  
- No need to expose `/.well-known/acme-challenge` publicly (though we can keep it as fallback)

Implementation:
- `certbot` container uses Cloudflare DNS plugin (API token in `.env`)
- Certificates stored in a shared Docker volume mounted into NGINX

### Docker services (compose)
- `app` (FastAPI)
- `nginx`
- `certbot` (for issue + renew)

Volumes:
- `letsencrypt-etc` (certs)
- `letsencrypt-var` (logs/work)

Ports:
- 80 and 443 exposed by NGINX

---

## 7) Security + operational guardrails

- No login. No uploads. No PII storage.
- Allowlist headers shown on `/debug` (avoid exposing cookies/auth headers).
- Add basic rate limiting in NGINX (protect the demo from abuse).
- Keep all secrets out of git:
  - Cloudflare DNS API token in `.env`
- Add a clear disclaimer footer on every page:
  - “Demo site for tutorials/testing only.”

---

## 8) How we’ll use this in content (ProbeOps integration)

Each Cloudflare tutorial should end with:

**“Validate in 2 minutes with ProbeOps”**
- Open **Horizon** in 2–3 regions side-by-side
- Visit `https://probeopslab.com/geo-redirect` and capture:
  - redirect chain
  - final landing path (`/ca` vs `/fi` etc.)
- Use **ProbeOps Terminal**:
  - `curl -I -L https://probeopslab.com/geo-redirect`
  - record status codes + Location chain per region
- Screenshot the `/debug` page to show detected geo + headers

---

## 9) Deployment checklist (one-time)

1. Provision VPS (Ubuntu)
2. Install Docker + Docker Compose plugin
3. Create repo folder: `cf-demo-site/`
4. Add `.env` with:
   - `DOMAIN=probeopslab.com`
   - `LE_EMAIL=<email>`
   - `CF_DNS_API_TOKEN=<cloudflare token with DNS edit permissions>`
5. `docker compose up -d nginx app`
6. Issue cert (certbot DNS-01) and reload NGINX
7. Turn Cloudflare proxy ON (if it was OFF)
8. Verify:
   - `https://probeopslab.com/` loads
   - `/debug` shows expected headers
   - redirect labs behave

---

## 10) Future expansion

- `vercel.demo.probeops.com` (Vercel geo headers + middleware labs)
- `fastly.demo.probeops.com`, etc.
- Keep the same endpoint pattern (`/debug`, `/redirect-lab`, `/geo-redirect`) so tutorials are consistent.
