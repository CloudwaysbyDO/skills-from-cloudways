#!/usr/bin/env python3
"""Outside-in website audit for agency prospecting.

Standard library only, so it runs on a managed agent host without installs.
Every check reports a measured value or "unknown"; nothing is guessed.

Usage:
    python site_audit.py https://example.com [--json] [--no-pagespeed]
"""
import argparse
import datetime as dt
import json
import os
import re
import socket
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (compatible; AgencySiteAudit/1.0)"
TIMEOUT = 15
MAX_BYTES = 3_000_000


def normalize(url):
    if not re.match(r"^https?://", url, re.I):
        url = "https://" + url
    return url.rstrip("/")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    start = time.time()
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        first = time.time()
        body = resp.read(MAX_BYTES)
        return {
            "final_url": resp.geturl(),
            "status": resp.status,
            "headers": {k.lower(): v for k, v in resp.headers.items()},
            "ttfb_s": round(first - start, 2),
            "body": body.decode("utf-8", errors="replace"),
            "bytes": len(body),
        }


def ssl_expiry(host):
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=TIMEOUT) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as s:
                cert = s.getpeercert()
        exp = dt.datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
        return {"valid": True, "expires": exp.date().isoformat(),
                "days_left": (exp - dt.datetime.utcnow()).days}
    except ssl.SSLCertVerificationError as e:
        return {"valid": False, "error": str(e.verify_message or e)[:120]}
    except Exception as e:  # noqa: BLE001
        return {"valid": None, "error": type(e).__name__}


def find(pattern, text, flags=re.I | re.S):
    m = re.search(pattern, text, flags)
    return m.group(1).strip() if m else None


def analyze_html(html):
    r = {}
    title = find(r"<title[^>]*>(.*?)</title>", html)
    r["title"] = re.sub(r"\s+", " ", title) if title else None
    r["title_length"] = len(r["title"]) if r["title"] else 0
    r["meta_description"] = find(
        r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']', html) or find(
        r'<meta[^>]+content=["\'](.*?)["\'][^>]+name=["\']description["\']', html)
    r["has_viewport"] = bool(re.search(r'<meta[^>]+name=["\']viewport["\']', html, re.I))
    r["h1_count"] = len(re.findall(r"<h1[\s>]", html, re.I))
    imgs = re.findall(r"<img\b[^>]*>", html, re.I)
    r["images"] = len(imgs)
    r["images_missing_alt"] = sum(1 for i in imgs if not re.search(r'\balt=["\'][^"\']+', i, re.I))

    gen = find(r'<meta[^>]+name=["\']generator["\'][^>]+content=["\'](.*?)["\']', html)
    r["generator"] = gen
    cms = None
    if gen:
        cms = gen
    elif "wp-content" in html or "wp-includes" in html:
        cms = "WordPress (version hidden)"
    elif "cdn.shopify.com" in html:
        cms = "Shopify"
    elif "static.wixstatic.com" in html:
        cms = "Wix"
    elif "squarespace" in html.lower():
        cms = "Squarespace"
    r["cms"] = cms
    wp_ver = find(r"WordPress\s+([\d.]+)", gen or "") or find(r"ver=(\d\.\d+(?:\.\d+)?)[\"'&][^>]*wp-includes", html)
    r["wordpress_version"] = wp_ver

    jq = find(r"jquery[.-]?(\d+\.\d+(?:\.\d+)?)(?:\.min)?\.js", html) or find(r"jquery\.js\?ver=(\d+\.\d+(?:\.\d+)?)", html)
    r["jquery_version"] = jq

    years = [int(y) for y in re.findall(r"(?:©|&copy;|copyright)\s*(?:\d{4}\s*[-–]\s*)?(20\d{2}|19\d{2})", html, re.I)]
    r["copyright_year"] = max(years) if years else None

    r["has_form"] = bool(re.search(r"<form\b", html, re.I))
    r["has_tel_link"] = "tel:" in html.lower()
    r["has_mailto"] = "mailto:" in html.lower()
    emails = set(re.findall(r"mailto:([\w.+-]+@[\w-]+\.[\w.-]+)", html, re.I))
    r["published_emails"] = sorted(emails)[:5]
    r["analytics"] = [n for n, p in [
        ("Google Analytics", r"gtag\(|google-analytics\.com|googletagmanager\.com/gtag"),
        ("Google Tag Manager", r"googletagmanager\.com/gtm"),
        ("Meta Pixel", r"connect\.facebook\.net"),
        ("Plausible", r"plausible\.io"),
    ] if re.search(p, html, re.I)]
    r["booking_widget"] = bool(re.search(r"calendly|acuityscheduling|booksy|opentable|resy|fresha|setmore|simplybook", html, re.I))
    return r


def pagespeed(url):
    key = os.environ.get("PAGESPEED_API_KEY")
    q = {"url": url, "strategy": "mobile", "category": "performance"}
    if key:
        q["key"] = key
    api = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?" + urllib.parse.urlencode(q)
    try:
        with urllib.request.urlopen(urllib.request.Request(api, headers={"User-Agent": UA}), timeout=60) as resp:
            data = json.loads(resp.read())
        lh = data["lighthouseResult"]
        audits = lh["audits"]
        return {
            "mobile_performance": round(lh["categories"]["performance"]["score"] * 100),
            "lcp_s": round(audits["largest-contentful-paint"]["numericValue"] / 1000, 1),
            "cls": round(audits["cumulative-layout-shift"]["numericValue"], 2),
        }
    except Exception as e:  # noqa: BLE001
        return {"error": f"PageSpeed unavailable ({type(e).__name__})"}


def build_findings(a):
    """Plain-language issues, each tied to a measured value. Severity: high/medium/low."""
    f = []
    this_year = dt.date.today().year
    if not a.get("https"):
        f.append(("high", "Site does not load securely over HTTPS; browsers label it 'Not secure'."))
    s = a.get("ssl", {})
    if s.get("valid") is False:
        f.append(("high", f"Security certificate is invalid ({s.get('error')})."))
    elif s.get("days_left") is not None and s["days_left"] < 30:
        f.append(("high", f"Security certificate expires in {s['days_left']} days ({s['expires']})."))
    h = a.get("html", {})
    if h and not h.get("has_viewport"):
        f.append(("high", "No mobile viewport tag; the page shows at desktop size on phones."))
    ps = a.get("pagespeed", {})
    if ps.get("mobile_performance") is not None:
        if ps["mobile_performance"] < 50:
            lcp = f"; main content takes {ps['lcp_s']}s to appear" if ps.get("lcp_s") else ""
            f.append(("high", f"Google PageSpeed mobile score is {ps['mobile_performance']}/100{lcp}."))
        elif ps["mobile_performance"] < 90:
            f.append(("medium", f"Google PageSpeed mobile score is {ps['mobile_performance']}/100."))
    if a.get("ttfb_s") and a["ttfb_s"] > 1.5:
        f.append(("medium", f"Server takes {a['ttfb_s']}s to start responding."))
    if a.get("bytes") and a["bytes"] > 500_000:
        f.append(("low", f"Homepage HTML alone is {round(a['bytes']/1024)} KB."))
    wp = h.get("wordpress_version")
    if wp:
        try:
            major = float(".".join(wp.split(".")[:2]))
            if major < 6.0:
                f.append(("high", f"Runs WordPress {wp}, an old version that no longer gets security fixes."))
        except ValueError:
            pass
    jq = h.get("jquery_version")
    if jq and jq.split(".")[0] in {"1", "2"}:
        f.append(("medium", f"Uses jQuery {jq}, a sign the site has not been updated in years."))
    cy = h.get("copyright_year")
    if cy and this_year - cy >= 2:
        f.append(("medium", f"Footer copyright says {cy}."))
    if h:
        if not h.get("title") or h.get("title", "").lower() in {"home", "homepage", "welcome"}:
            f.append(("medium", f"Page title is weak or missing ('{h.get('title') or 'none'}')."))
        elif h.get("title_length", 0) > 65:
            f.append(("low", f"Page title is {h['title_length']} characters and gets cut off in Google."))
        if not h.get("meta_description"):
            f.append(("medium", "No meta description; Google picks random text for the search snippet."))
        if h.get("h1_count") == 0:
            f.append(("low", "No main H1 heading on the homepage."))
        if h.get("images") and h.get("images_missing_alt", 0) >= max(3, h["images"] // 2):
            f.append(("low", f"{h['images_missing_alt']} of {h['images']} images have no alt text."))
        if not h.get("has_form") and not h.get("has_tel_link"):
            f.append(("medium", "No contact form or tap-to-call phone link on the homepage."))
        if not h.get("analytics"):
            f.append(("low", "No analytics detected; the owner cannot see where visitors come from."))
    return [{"severity": s, "finding": t} for s, t in f]


def audit(url, use_pagespeed=True):
    url = normalize(url)
    host = urllib.parse.urlparse(url).hostname
    a = {"input_url": url, "domain": host, "audited_at": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z"}
    page = None
    try:
        page = fetch(url)
        a["https"] = page["final_url"].startswith("https://")
    except Exception as e:  # noqa: BLE001
        a["https_error"] = type(e).__name__
        try:
            page = fetch(url.replace("https://", "http://", 1))
            a["https"] = page["final_url"].startswith("https://")
        except Exception as e2:  # noqa: BLE001
            a["reachable"] = False
            a["error"] = f"Could not load site ({type(e2).__name__})"
            a["findings"] = []
            return a
    a["reachable"] = True
    a.update({k: page[k] for k in ("final_url", "status", "ttfb_s", "bytes")})
    a["server"] = page["headers"].get("server")
    a["ssl"] = ssl_expiry(host) if a["https"] or a.get("https_error") else {"valid": None}
    a["html"] = analyze_html(page["body"])
    if use_pagespeed:
        a["pagespeed"] = pagespeed(a["final_url"])
    a["findings"] = build_findings(a)
    a["severity_counts"] = {s: sum(1 for x in a["findings"] if x["severity"] == s) for s in ("high", "medium", "low")}
    return a


def main():
    p = argparse.ArgumentParser()
    p.add_argument("url")
    p.add_argument("--json", action="store_true")
    p.add_argument("--no-pagespeed", action="store_true")
    args = p.parse_args()
    result = audit(args.url, not args.no_pagespeed)
    if args.json:
        print(json.dumps(result, indent=2))
        return
    print(f"Audit: {result['input_url']}")
    if not result.get("reachable"):
        print("  " + result.get("error", "unreachable"))
        sys.exit(1)
    for f in result["findings"]:
        print(f"  [{f['severity']}] {f['finding']}")
    if not result["findings"]:
        print("  No significant issues found.")


if __name__ == "__main__":
    main()