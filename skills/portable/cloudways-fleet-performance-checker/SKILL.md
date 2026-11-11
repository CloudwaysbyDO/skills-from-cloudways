---
name: cloudways-fleet-performance-checker
description: Full performance audit of all Cloudways apps via MCP APIs.
version: 0.2.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cloudways, performance, wordpress, magento, web-vitals, security]
    related_skills: [cloudways-performance-audit]
---

# Cloudways Fleet Performance Checker

Runs a complete performance audit across every app on a Cloudways server: server specs, PHP/DB config, service health, disk/bandwidth, WordPress version + vulnerabilities, Google PageSpeed Insights (mobile + desktop), and a prioritised action plan. Works for WordPress and Magento apps. PSI works with `*.cloudwaysapps.com` staging URLs when an API key is provided — no custom domain needed.

## When to Use

- User asks for a "full performance check" or "performance report" on their Cloudways account
- Auditing server health, PHP config, or DB settings
- Checking for WordPress plugin/theme vulnerabilities across apps
- Benchmarking before/after an infrastructure change

Don't use for: single-app targeted debugging (use `cloudways-performance-audit`), or non-Cloudways hosts.

## Prerequisites

- Cloudways MCP configured (`mcp__cloudways__*` tools available)
- Google PageSpeed Insights API key (GCP Console → APIs & Services → Credentials). Store in `~/.hermes/.env` as `PSI_API_KEY=<key>`. Without a key, PSI uses anonymous quota (25 req/day shared — exhausts quickly). With a key, quota is 25,000 req/day per project.

## Procedure

### Step 1 — Discover server and apps

1. `tool_call` → `mcp__cloudways__server_list` — note every server ID and label
2. `tool_call` → `mcp__cloudways__app_list` — note app IDs, labels, types (wordpress/magento), and FQDNs
3. Focus WordPress and Magento apps; record both for the report

### Step 2 — Server-level data (run all in sequence or via delegate_task)

4. `tool_call` → `mcp__cloudways__server_get` with `{"server_id": "<id>"}` — specs (cloud, region, size, OS, IP)
5. `tool_call` → `mcp__cloudways__server_settings_get` — PHP version, memory_limit, execution_limit, upload_size, display_errors, MariaDB charset/connections
6. `tool_call` → `mcp__cloudways__service_status` — nginx, mysql, php-fpm, redis, memcached, varnish, imunify360, new relic
7. `tool_call` → `mcp__cloudways__monitoring_server_summary` with `type: "db"` — per-app disk usage
8. `tool_call` → `mcp__cloudways__monitoring_server_summary` with `type: "bw"` — monthly bandwidth

### Step 3 — Per-app data

For each app:
9. `tool_call` → `mcp__cloudways__app_get` with `{"app_id": "<id>"}` — version, active theme, redis_acl_status
10. `tool_call` → `mcp__cloudways__varnish_app_status` — whether Varnish is enabled per app
11. `tool_call` → `mcp__cloudways__app_vulnerabilities_list` *(WordPress only)* — core, theme, plugin CVEs with CVSS scores and fix versions

### Step 4 — Google PageSpeed Insights

PSI works with both custom domains and `*.cloudwaysapps.com` staging URLs **when an API key is supplied**. Without a key, anonymous quota exhausts quickly (HTTP 429) and staging URLs may fail DNS resolution from Google's infrastructure.

Run mobile + desktop for every app using `terminal` with sequential `curl` calls (do NOT use `&` backgrounding — use sequential calls or a single shell script without `&`):

```bash
API_KEY="<key>"
BASE="https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

curl -s "$BASE?url=<APP_URL>&strategy=mobile&category=performance&key=$API_KEY" -o /tmp/psi_<app>_mobile.json
curl -s "$BASE?url=<APP_URL>&strategy=desktop&category=performance&key=$API_KEY" -o /tmp/psi_<app>_desktop.json
```

Run all apps sequentially in one `terminal` call with `timeout=300`. Then parse results with `execute_code`:

```python
import json, pathlib

def extract(path):
    d = json.loads(pathlib.Path(path).read_text())
    if "error" in d:
        return {"error": d["error"]["message"]}
    lr = d.get("lighthouseResult", {})
    audits = lr.get("audits", {})
    score = lr.get("categories", {}).get("performance", {}).get("score")
    def av(k): return audits.get(k, {}).get("displayValue", "N/A")
    opp_keys = ["render-blocking-resources", "unused-css-rules", "unused-javascript",
                "uses-optimized-images", "uses-text-compression", "uses-long-cache-ttl"]
    opps = []
    for k in opp_keys:
        a = audits.get(k, {})
        if a and a.get("score", 1) < 0.9:
            sb = a.get("details", {}).get("overallSavingsBytes", 0)
            sm = a.get("details", {}).get("overallSavingsMs", 0)
            opps.append(f"{a.get('title', k)} — {sm:.0f}ms" if sm else f"{a.get('title', k)} — {sb/1024:.0f} KB")
    return {
        "score": round(score * 100) if score else "N/A",
        "FCP": av("first-contentful-paint"), "LCP": av("largest-contentful-paint"),
        "TBT": av("total-blocking-time"), "CLS": av("cumulative-layout-shift"),
        "SI": av("speed-index"), "TTI": av("interactive"),
        "opportunities": opps,
    }
```

If quota exhausted (HTTP 429 in the JSON `error` field), note it in the report and skip. Do not retry.

### Step 6 — Compile the report

Structure the final report in this order:
1. **Server Infrastructure** — specs, PHP settings, MariaDB settings, service status, disk/BW
2. **Application Overview** — version, theme, Varnish, Object Cache per app
3. **PSI Results** — Core Web Vitals, scores, opportunities; note if skipped and why
4. **Security — Vulnerabilities** — per WordPress app; note Magento needs external scanning
5. **Prioritised Action Plan** — 🔴 Fix Immediately / 🟠 Fix Soon / 💡 Optimise

## Key Findings to Flag

- `character_set_server = latin1` → **should be `utf8mb4`** for WordPress/WooCommerce
- PHP EOL versions running (8.0 is EOL) → security risk
- `date.timezone` empty → PHP date/time warnings
- New Relic sysmond stopped → monitoring gap if intentional
- Breeze Cache or Redux Framework with known CVEs (CVSS ≥ 6) → patch immediately
- Magento with >100 JS requests → JS bundling not enabled
- Any app with no CDN → recommend Cloudflare
- `cache-control: no-store` on Magento → blocks bfcache

## Pitfalls

- **PSI without API key fails on staging URLs**: Anonymous PSI quota exhausts at 25 req/day and `*.cloudwaysapps.com` may not resolve. Always use a `&key=` API key — it lifts quota to 25,000/day and resolves the DNS issue.
- **PSI quota exhaustion with key**: HTTP 429 in the response JSON `error.code` field means the key's daily quota is hit. Check GCP Console for quota usage.
- **Do not use `&` shell backgrounding for curl PSI calls**: The terminal tool rejects foreground commands with `&`. Run all curl calls sequentially in one `terminal(command=..., timeout=300)` call instead.
- **Vulnerability scan is WordPress-only**: `mcp__cloudways__app_vulnerabilities_list` returns an error for Magento apps — skip it and note in the report.
- **`server_settings_get` returns PHP settings for the server default** — individual apps may run a different PHP version (check `app_get` response and service_status for multiple php-fpm versions).
- **delegate_task iteration cap**: Steps 2–3 are 8+ tool calls; subagents hit the iteration cap at ~5. Either run server-level and app-level calls in the parent, or split into two smaller delegate_task batches.

## Verification

Report is complete when:
- [ ] All apps listed in `app_list` have PSI mobile + desktop scores (or quota/DNS failure noted with reason)
- [ ] All WordPress apps have a vulnerability count (even if 0)
- [ ] Server PHP and MariaDB settings are documented
- [ ] Service status table covers nginx, mysql, php-fpm, redis, varnish at minimum
- [ ] Action plan items are each linked to a specific finding

