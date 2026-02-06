"""
ProbeOps Lab - CDN/DevOps Testing Utility
https://probeopslab.com
"""

import asyncio
import hashlib
import json
import os
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, Request, Response, Path
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="ProbeOps Lab", docs_url=None, redoc_url=None)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Umami analytics website ID (set after creating the site in Umami dashboard)
UMAMI_WEBSITE_ID = os.environ.get("UMAMI_WEBSITE_ID", "")
templates.env.globals["umami_website_id"] = UMAMI_WEBSITE_ID

# Allowed headers for /debug endpoint (security: no cookies/auth)
# Note: x-real-ip removed as it shows Cloudflare edge IP, not user IP (confusing)
ALLOWED_HEADERS = [
    "host",
    "x-forwarded-for",
    "x-forwarded-proto",
    "cf-ray",
    "cf-ipcountry",
    "cf-ipcity",
    "cf-ipcontinent",
    "cf-region",
    "cf-connecting-ip",
    "user-agent",
    "accept-language",
    "accept-encoding",
    "cf-cache-status",
    "cf-worker",
]

# Cache endpoint configurations
CACHE_CONFIGS = {
    "public-short": {"cache_control": "public, max-age=60", "description": "Public cache, 60 second max-age"},
    "public-long": {"cache_control": "public, max-age=86400", "description": "Public cache, 24 hour max-age"},
    "no-store": {"cache_control": "no-store", "description": "No caching allowed"},
    "no-cache": {"cache_control": "no-cache", "description": "Must revalidate before using cached version"},
    "private": {"cache_control": "private, max-age=60", "description": "Private cache only (browser), not shared (CDN)"},
    "s-maxage": {"cache_control": "public, max-age=60, s-maxage=300", "description": "Browser: 60s, CDN/shared cache: 300s"},
    "stale-while-revalidate": {"cache_control": "public, max-age=60, stale-while-revalidate=300", "description": "Serve stale while revalidating in background"},
    "immutable": {"cache_control": "public, max-age=31536000, immutable", "description": "Immutable content, cache for 1 year"},
}


def get_request_context(request: Request) -> dict:
    """Extract sanitized request context for display."""
    headers = {}
    for key in ALLOWED_HEADERS:
        value = request.headers.get(key)
        if value:
            # Truncate user-agent to 100 chars
            if key == "user-agent" and len(value) > 100:
                value = value[:100] + "..."
            headers[key] = value

    return {
        "request_id": str(uuid4())[:8],
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "method": request.method,
        "scheme": request.headers.get("x-forwarded-proto", request.url.scheme),
        "host": request.headers.get("host", request.url.hostname),
        "path": request.url.path,
        "query": str(request.query_params) if request.query_params else None,
        "headers": headers,
        "client_ip": request.headers.get("cf-connecting-ip")
        or request.headers.get("x-real-ip")
        or request.client.host
        if request.client
        else "unknown",
        "country": request.headers.get("cf-ipcountry", "N/A"),
        "city": request.headers.get("cf-ipcity", "N/A"),
        "region": request.headers.get("cf-region", "N/A"),
        "cf_ray": request.headers.get("cf-ray", "N/A"),
    }


# =============================================================================
# Core Pages
# =============================================================================


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Lab home page with links to all labs."""
    ctx = get_request_context(request)
    return templates.TemplateResponse("index.html", {"request": request, "ctx": ctx, "active_page": "home"})


@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    """About page - explains what this lab is and who maintains it."""
    ctx = get_request_context(request)
    return templates.TemplateResponse("about.html", {"request": request, "ctx": ctx, "active_page": "about"})


@app.get("/use-cases", response_class=HTMLResponse)
async def use_cases(request: Request):
    """Use cases - real problems you can troubleshoot with this lab."""
    ctx = get_request_context(request)
    return templates.TemplateResponse("use-cases.html", {"request": request, "ctx": ctx, "active_page": "use-cases"})


@app.get("/debug", response_class=HTMLResponse)
async def debug(request: Request):
    """Request and geo debug page - sanitized headers display."""
    ctx = get_request_context(request)
    return templates.TemplateResponse("debug.html", {"request": request, "ctx": ctx, "active_page": "debug"})


@app.get("/debug.json")
async def debug_json(request: Request):
    """JSON version of debug info for programmatic/CLI access."""
    ctx = get_request_context(request)
    json_ctx = {
        "client_ip": ctx["client_ip"],
        "country": ctx["country"],
        "city": ctx["city"],
        "region": ctx["region"],
        "method": ctx["method"],
        "scheme": ctx["scheme"],
        "host": ctx["host"],
        "path": ctx["path"],
        "query": ctx["query"],
        "headers": ctx["headers"],
        "cf_ray": ctx["cf_ray"],
        "timestamp": ctx["timestamp"],
        "request_id": ctx["request_id"],
    }
    return Response(
        content=json.dumps(json_ctx, indent=2),
        media_type="application/json"
    )


@app.api_route("/echo", methods=["GET", "HEAD"])
async def echo_endpoint(request: Request):
    """Echo endpoint showing request info with useful response headers."""
    ctx = get_request_context(request)

    body = {
        "request": {
            "client_ip": ctx["client_ip"],
            "country": ctx["country"],
            "method": ctx["method"],
            "scheme": ctx["scheme"],
            "host": ctx["host"],
            "path": ctx["path"],
            "headers": ctx["headers"],
        },
        "response_headers": {
            "note": "Check response headers with: curl -sI or curl -sD -",
            "headers_included": [
                "X-Request-Id",
                "X-Client-IP",
                "X-Country",
                "X-Served-By",
            ]
        },
        "timestamp": ctx["timestamp"],
    }

    response = Response(
        content=json.dumps(body, indent=2),
        media_type="application/json"
    )
    response.headers["X-Request-Id"] = ctx["request_id"]
    response.headers["X-Client-IP"] = ctx["client_ip"]
    response.headers["X-Country"] = ctx["country"]
    response.headers["X-Served-By"] = "probeopslab"
    return response


@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots():
    """Allow indexing for public pages, block API/utility endpoints."""
    return """User-agent: *
Allow: /
Disallow: /debug.json
Disallow: /echo
Disallow: /r/
Disallow: /final
Disallow: /delay/
Disallow: /status/
Disallow: /size/
Disallow: /us
Disallow: /ca
Disallow: /fi
Disallow: /row
Disallow: /host-lab
Sitemap: https://probeopslab.com/sitemap.xml"""


@app.get("/sitemap.xml")
async def sitemap():
    """XML sitemap for search engine discovery."""
    pages = [
        {"loc": "/", "priority": "1.0", "changefreq": "weekly"},
        {"loc": "/debug", "priority": "0.8", "changefreq": "monthly"},
        {"loc": "/cache", "priority": "0.8", "changefreq": "monthly"},
        {"loc": "/redirect-lab", "priority": "0.8", "changefreq": "monthly"},
        {"loc": "/tools", "priority": "0.8", "changefreq": "monthly"},
        {"loc": "/geo-redirect", "priority": "0.7", "changefreq": "monthly"},
        {"loc": "/use-cases", "priority": "0.7", "changefreq": "monthly"},
        {"loc": "/about", "priority": "0.5", "changefreq": "monthly"},
    ]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for p in pages:
        xml += f'  <url>\n'
        xml += f'    <loc>https://probeopslab.com{p["loc"]}</loc>\n'
        xml += f'    <changefreq>{p["changefreq"]}</changefreq>\n'
        xml += f'    <priority>{p["priority"]}</priority>\n'
        xml += f'  </url>\n'
    xml += '</urlset>'
    return Response(content=xml, media_type="application/xml")


# =============================================================================
# Cache Labs
# =============================================================================


@app.get("/cache", response_class=HTMLResponse)
async def cache_lab(request: Request):
    """Cache lab index page with documentation."""
    ctx = get_request_context(request)
    return templates.TemplateResponse("cache_lab.html", {"request": request, "ctx": ctx, "cache_configs": CACHE_CONFIGS, "active_page": "cache"})


def create_cache_response(path: str, cache_control: str, description: str) -> Response:
    """Create a JSON response with appropriate cache headers."""
    now = datetime.now(timezone.utc)
    body = {"path": path, "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "cache_control": cache_control, "description": description}
    etag = hashlib.md5(str(body).encode()).hexdigest()[:16]
    response = Response(
        content=json.dumps(body, indent=2),
        media_type="application/json"
    )
    response.headers["Cache-Control"] = cache_control
    response.headers["ETag"] = f'"{etag}"'
    response.headers["Last-Modified"] = now.strftime("%a, %d %b %Y %H:%M:%S GMT")
    response.headers["X-Cache-Test"] = "probeopslab"
    return response


@app.api_route("/cache/public-short", methods=["GET", "HEAD"])
async def cache_public_short():
    c = CACHE_CONFIGS["public-short"]
    return create_cache_response("/cache/public-short", c["cache_control"], c["description"])


@app.api_route("/cache/public-long", methods=["GET", "HEAD"])
async def cache_public_long():
    c = CACHE_CONFIGS["public-long"]
    return create_cache_response("/cache/public-long", c["cache_control"], c["description"])


@app.api_route("/cache/no-store", methods=["GET", "HEAD"])
async def cache_no_store():
    c = CACHE_CONFIGS["no-store"]
    return create_cache_response("/cache/no-store", c["cache_control"], c["description"])


@app.api_route("/cache/no-cache", methods=["GET", "HEAD"])
async def cache_no_cache():
    c = CACHE_CONFIGS["no-cache"]
    return create_cache_response("/cache/no-cache", c["cache_control"], c["description"])


@app.api_route("/cache/private", methods=["GET", "HEAD"])
async def cache_private():
    c = CACHE_CONFIGS["private"]
    return create_cache_response("/cache/private", c["cache_control"], c["description"])


@app.api_route("/cache/s-maxage", methods=["GET", "HEAD"])
async def cache_s_maxage():
    c = CACHE_CONFIGS["s-maxage"]
    return create_cache_response("/cache/s-maxage", c["cache_control"], c["description"])


@app.api_route("/cache/stale-while-revalidate", methods=["GET", "HEAD"])
async def cache_stale_while_revalidate():
    c = CACHE_CONFIGS["stale-while-revalidate"]
    return create_cache_response("/cache/stale-while-revalidate", c["cache_control"], c["description"])


@app.api_route("/cache/immutable", methods=["GET", "HEAD"])
async def cache_immutable():
    c = CACHE_CONFIGS["immutable"]
    return create_cache_response("/cache/immutable", c["cache_control"], c["description"])


# =============================================================================
# Redirect Labs
# =============================================================================


@app.get("/redirect-lab", response_class=HTMLResponse)
async def redirect_lab(request: Request):
    """Redirect lab menu with links to all redirect tests."""
    ctx = get_request_context(request)
    return templates.TemplateResponse(
        "redirect_lab.html", {"request": request, "ctx": ctx, "active_page": "redirects"}
    )


@app.api_route("/r/301", methods=["GET", "HEAD"])
async def redirect_301():
    """301 Permanent redirect to /final."""
    return RedirectResponse(url="/final", status_code=301)


@app.api_route("/r/302", methods=["GET", "HEAD"])
async def redirect_302():
    """302 Found redirect to /final."""
    return RedirectResponse(url="/final", status_code=302)


@app.api_route("/r/307", methods=["GET", "HEAD"])
async def redirect_307():
    """307 Temporary redirect to /final."""
    return RedirectResponse(url="/final", status_code=307)


@app.api_route("/r/308", methods=["GET", "HEAD"])
async def redirect_308():
    """308 Permanent redirect to /final."""
    return RedirectResponse(url="/final", status_code=308)


@app.get("/final", response_class=HTMLResponse)
async def final(request: Request):
    """Final landing page after redirects."""
    ctx = get_request_context(request)
    return templates.TemplateResponse("final.html", {"request": request, "ctx": ctx})


# =============================================================================
# Geo Routing Labs
# =============================================================================


@app.get("/geo-redirect", response_class=HTMLResponse)
async def geo_redirect(request: Request):
    """
    Geo redirect entry point.
    This page is designed to be the target of Cloudflare Redirect Rules.
    The actual geo-based redirects happen at Cloudflare edge.
    """
    ctx = get_request_context(request)
    return templates.TemplateResponse(
        "geo_redirect.html", {"request": request, "ctx": ctx}
    )


@app.get("/us", response_class=HTMLResponse)
async def region_us(request: Request):
    """US region landing page."""
    ctx = get_request_context(request)
    return templates.TemplateResponse(
        "region.html",
        {
            "request": request,
            "ctx": ctx,
            "region_code": "US",
            "region_name": "United States",
            "region_emoji": "🇺🇸",
        },
    )


@app.get("/ca", response_class=HTMLResponse)
async def region_ca(request: Request):
    """Canada region landing page."""
    ctx = get_request_context(request)
    return templates.TemplateResponse(
        "region.html",
        {
            "request": request,
            "ctx": ctx,
            "region_code": "CA",
            "region_name": "Canada",
            "region_emoji": "🇨🇦",
        },
    )


@app.get("/fi", response_class=HTMLResponse)
async def region_fi(request: Request):
    """Finland region landing page."""
    ctx = get_request_context(request)
    return templates.TemplateResponse(
        "region.html",
        {
            "request": request,
            "ctx": ctx,
            "region_code": "FI",
            "region_name": "Finland",
            "region_emoji": "🇫🇮",
        },
    )


@app.get("/row", response_class=HTMLResponse)
async def region_row(request: Request):
    """Rest of World region landing page."""
    ctx = get_request_context(request)
    return templates.TemplateResponse(
        "region.html",
        {
            "request": request,
            "ctx": ctx,
            "region_code": "ROW",
            "region_name": "Rest of World",
            "region_emoji": "🌍",
        },
    )


# =============================================================================
# Host Lab
# =============================================================================


@app.api_route("/host-lab", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def host_lab(request: Request):
    """Host and scheme helper - shows current host and links to variants."""
    ctx = get_request_context(request)
    return templates.TemplateResponse(
        "host_lab.html", {"request": request, "ctx": ctx}
    )


# =============================================================================
# Utility Labs (Timing, Status, Size)
# =============================================================================

# Allowed status codes for /status endpoint
ALLOWED_STATUS_CODES = [200, 201, 204, 400, 401, 403, 404, 405, 408, 429, 500, 502, 503, 504]


@app.get("/tools", response_class=HTMLResponse)
async def tools_lab(request: Request):
    """Utility tools lab index page."""
    ctx = get_request_context(request)
    return templates.TemplateResponse("tools_lab.html", {"request": request, "ctx": ctx, "active_page": "tools"})


@app.get("/delay/{ms}")
async def delay_endpoint(ms: int = Path(..., ge=0, le=10000)):
    """Return response after specified delay in milliseconds (max 10000ms)."""
    start_time = datetime.now(timezone.utc)
    await asyncio.sleep(ms / 1000)
    end_time = datetime.now(timezone.utc)

    body = {
        "path": f"/delay/{ms}",
        "requested_delay_ms": ms,
        "actual_delay_ms": round((end_time - start_time).total_seconds() * 1000),
        "started_at": start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "completed_at": end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    }
    return Response(
        content=json.dumps(body, indent=2),
        media_type="application/json"
    )


@app.api_route("/status/{code}", methods=["GET", "HEAD"])
async def status_endpoint(code: int = Path(...)):
    """Return specified HTTP status code."""
    if code not in ALLOWED_STATUS_CODES:
        body = {
            "error": "Invalid status code",
            "requested_code": code,
            "allowed_codes": ALLOWED_STATUS_CODES,
        }
        return Response(
            content=json.dumps(body, indent=2),
            media_type="application/json",
            status_code=400
        )

    # Status code descriptions
    descriptions = {
        200: "OK",
        201: "Created",
        204: "No Content",
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        408: "Request Timeout",
        429: "Too Many Requests",
        500: "Internal Server Error",
        502: "Bad Gateway",
        503: "Service Unavailable",
        504: "Gateway Timeout",
    }

    body = {
        "path": f"/status/{code}",
        "status_code": code,
        "status_text": descriptions.get(code, "Unknown"),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    # 204 No Content should not have a body
    if code == 204:
        return Response(status_code=204)

    return Response(
        content=json.dumps(body, indent=2),
        media_type="application/json",
        status_code=code
    )


@app.get("/size/{bytes}.json")
async def size_json_endpoint(bytes: int = Path(..., ge=0, le=1048576)):
    """Return metadata about what /size/{bytes} would return (no binary payload)."""
    body = {
        "path": f"/size/{bytes}",
        "requested_bytes": bytes,
        "actual_endpoint": f"/size/{bytes}",
        "content_type": "application/octet-stream",
        "description": f"Use GET /size/{bytes} to receive a {bytes}-byte binary response",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    return Response(
        content=json.dumps(body, indent=2),
        media_type="application/json"
    )


@app.api_route("/size/{bytes}", methods=["GET", "HEAD"])
async def size_endpoint(bytes: int = Path(..., ge=0, le=1048576)):
    """Return response of specified size in bytes (max 1MB = 1048576 bytes)."""
    # Create JSON header
    header = {
        "path": f"/size/{bytes}",
        "requested_bytes": bytes,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    header_json = json.dumps(header, indent=2)
    header_size = len(header_json.encode('utf-8'))

    # Calculate padding needed
    if bytes <= header_size:
        # If requested size is smaller than header, just return header
        content = header_json
    else:
        # Add padding to reach requested size
        padding_needed = bytes - header_size - 2  # -2 for newline and closing
        padding = "X" * max(0, padding_needed)
        content = header_json[:-1] + f',\n  "padding": "{padding}"\n}}'

    # Trim or pad to exact size
    content_bytes = content.encode('utf-8')
    if len(content_bytes) < bytes:
        content = content + "X" * (bytes - len(content_bytes))
    elif len(content_bytes) > bytes:
        content = content_bytes[:bytes].decode('utf-8', errors='ignore')

    return Response(
        content=content,
        media_type="application/octet-stream",
        headers={"Content-Length": str(bytes)}
    )
