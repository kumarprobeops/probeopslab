"""
CF Demo Site - Cloudflare Redirect & Geo Labs
https://probeopslab.com
"""

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="CF Demo Labs", docs_url=None, redoc_url=None)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Allowed headers for /debug endpoint (security: no cookies/auth)
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
    return templates.TemplateResponse("index.html", {"request": request, "ctx": ctx})


@app.get("/debug", response_class=HTMLResponse)
async def debug(request: Request):
    """Request and geo debug page - sanitized headers display."""
    ctx = get_request_context(request)
    return templates.TemplateResponse("debug.html", {"request": request, "ctx": ctx})


@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots():
    """Disallow all indexing for demo site."""
    return "User-agent: *\nDisallow: /"


# =============================================================================
# Redirect Labs
# =============================================================================


@app.get("/redirect-lab", response_class=HTMLResponse)
async def redirect_lab(request: Request):
    """Redirect lab menu with links to all redirect tests."""
    ctx = get_request_context(request)
    return templates.TemplateResponse(
        "redirect_lab.html", {"request": request, "ctx": ctx}
    )


@app.get("/r/301")
async def redirect_301():
    """301 Permanent redirect to /final."""
    return RedirectResponse(url="/final", status_code=301)


@app.get("/r/302")
async def redirect_302():
    """302 Found redirect to /final."""
    return RedirectResponse(url="/final", status_code=302)


@app.get("/r/307")
async def redirect_307():
    """307 Temporary redirect to /final."""
    return RedirectResponse(url="/final", status_code=307)


@app.get("/r/308")
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


@app.get("/host-lab", response_class=HTMLResponse)
async def host_lab(request: Request):
    """Host and scheme helper - shows current host and links to variants."""
    ctx = get_request_context(request)
    return templates.TemplateResponse(
        "host_lab.html", {"request": request, "ctx": ctx}
    )
