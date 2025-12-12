# Curl Command Reference

Quick reference for testing endpoints. Replace `localhost:8000` with your domain.

## Debug / IP Info

```bash
# Get your IP and geo info (human readable)
curl https://localhost:8000/debug

# Get as JSON (for scripts)
curl -s https://localhost:8000/debug.json | jq .

# Just IP and country
curl -s https://localhost:8000/debug.json | jq '{ip: .client_ip, country: .country}'

# Check what headers reach the server
curl -s https://localhost:8000/debug.json | jq .headers
```

## Redirects

```bash
# Check redirect status codes (use -I for headers only)
curl -sI https://localhost:8000/r/301 | grep -i "HTTP\|location"
curl -sI https://localhost:8000/r/302 | grep -i "HTTP\|location"
curl -sI https://localhost:8000/r/307 | grep -i "HTTP\|location"
curl -sI https://localhost:8000/r/308 | grep -i "HTTP\|location"

# Follow redirects and show each hop
curl -sIL https://localhost:8000/r/301 | grep -i "HTTP\|location"

# Test POST redirect behavior (307/308 preserve method, 301/302 may not)
curl -X POST -sI https://localhost:8000/r/307 | grep -i "HTTP\|location"
```

## HTTP Status Codes

```bash
# Get specific status codes
curl -sI https://localhost:8000/status/200 | grep HTTP
curl -sI https://localhost:8000/status/201 | grep HTTP
curl -sI https://localhost:8000/status/204 | grep HTTP
curl -sI https://localhost:8000/status/400 | grep HTTP
curl -sI https://localhost:8000/status/401 | grep HTTP
curl -sI https://localhost:8000/status/403 | grep HTTP
curl -sI https://localhost:8000/status/404 | grep HTTP
curl -sI https://localhost:8000/status/408 | grep HTTP
curl -sI https://localhost:8000/status/429 | grep HTTP
curl -sI https://localhost:8000/status/500 | grep HTTP
curl -sI https://localhost:8000/status/502 | grep HTTP
curl -sI https://localhost:8000/status/503 | grep HTTP
curl -sI https://localhost:8000/status/504 | grep HTTP
```

## Delays / Timeouts

```bash
# Simulate slow backend (milliseconds)
curl -w "Time: %{time_total}s\n" https://localhost:8000/delay/1000
curl -w "Time: %{time_total}s\n" https://localhost:8000/delay/3000
curl -w "Time: %{time_total}s\n" https://localhost:8000/delay/5000

# Test your client's timeout (should fail if timeout < delay)
curl --max-time 2 https://localhost:8000/delay/5000

# Find your load balancer's timeout threshold
for delay in 5000 10000 15000 30000; do
  echo "Testing ${delay}ms..."
  curl -sI --max-time 60 -w "Time: %{time_total}s\n" \
    https://localhost:8000/delay/$delay | grep -E "HTTP|Time"
done
```

## Response Size

```bash
# Get specific payload sizes (bytes)
curl -o /dev/null -w "Size: %{size_download} bytes, Time: %{time_total}s\n" \
  https://localhost:8000/size/1024

curl -o /dev/null -w "Size: %{size_download} bytes, Time: %{time_total}s\n" \
  https://localhost:8000/size/102400

curl -o /dev/null -w "Size: %{size_download} bytes, Time: %{time_total}s\n" \
  https://localhost:8000/size/1048576

# Get size metadata as JSON
curl -s https://localhost:8000/size/1024.json | jq .
```

## Cache Headers

```bash
# Test different Cache-Control configurations
curl -sI https://localhost:8000/cache/public-short | grep -i "cache-control"
curl -sI https://localhost:8000/cache/public-long | grep -i "cache-control"
curl -sI https://localhost:8000/cache/no-store | grep -i "cache-control"
curl -sI https://localhost:8000/cache/no-cache | grep -i "cache-control"
curl -sI https://localhost:8000/cache/private | grep -i "cache-control"
curl -sI https://localhost:8000/cache/s-maxage | grep -i "cache-control"
curl -sI https://localhost:8000/cache/stale-while-revalidate | grep -i "cache-control"
curl -sI https://localhost:8000/cache/immutable | grep -i "cache-control"

# Test CDN caching (run twice, second should show HIT if behind CDN)
curl -sI https://localhost:8000/static/styles.css | grep -i "cf-cache-status"
curl -sI https://localhost:8000/static/styles.css | grep -i "cf-cache-status"
```

## CDN / Cloudflare Specific

```bash
# Check Cloudflare headers
curl -sI https://localhost:8000/ | grep -i "cf-"

# Get Cloudflare Ray ID
curl -sI https://localhost:8000/ | grep -i "cf-ray"

# Check cache status
curl -sI https://localhost:8000/static/styles.css | grep -i "cf-cache-status"
```

## SSL / HTTPS

```bash
# Check SSL certificate
curl -vI https://localhost:8000 2>&1 | grep -A 5 "Server certificate"

# Test HTTP to HTTPS redirect
curl -sI http://localhost:8000/ | grep -i "HTTP\|location"

# Test www to apex redirect
curl -sI https://www.localhost:8000/ | grep -i "HTTP\|location"
```

## Useful curl Options

| Option | Description |
|--------|-------------|
| `-s` | Silent mode (no progress bar) |
| `-I` | Fetch headers only (HEAD request) |
| `-L` | Follow redirects |
| `-w` | Custom output format |
| `-o /dev/null` | Discard response body |
| `--max-time N` | Timeout after N seconds |
| `-H "Header: value"` | Add custom header |
| `-X POST` | Use POST method |

## Output Format Variables

Use with `-w` option:

| Variable | Description |
|----------|-------------|
| `%{http_code}` | HTTP status code |
| `%{time_total}` | Total time in seconds |
| `%{time_connect}` | Time to connect |
| `%{time_starttransfer}` | Time to first byte |
| `%{size_download}` | Downloaded bytes |
| `%{speed_download}` | Download speed (bytes/sec) |

Example:
```bash
curl -s -o /dev/null -w "Status: %{http_code}, Time: %{time_total}s, Size: %{size_download} bytes\n" \
  https://localhost:8000/debug
```
