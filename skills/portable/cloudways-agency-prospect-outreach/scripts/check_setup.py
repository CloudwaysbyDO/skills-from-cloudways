#!/usr/bin/env python3
"""Preflight check for agency-prospect-outreach.

Reports which keys and settings are present and, where cheap, whether they work.
Never prints secret values.

Usage:
    python check_setup.py [--profile agency-profile.md] [--no-network] [--json]
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

UA = "AgencyProspectSetup/1.0"

KEYS = {
    "PAGESPEED_API_KEY": "Google PageSpeed (recommended)",
    "AGENTMAIL_API_KEY": "AgentMail API (if no AgentMail tool or MCP)",
    "BRAVE_API_KEY": "Brave web search (optional)",
    "SERPER_API_KEY": "Serper web search (optional)",
    "FIRECRAWL_API_KEY": "Firecrawl page extraction (optional)",
    "HUNTER_API_KEY": "Hunter email enrichment (optional)",
    "APOLLO_API_KEY": "Apollo enrichment (optional)",
}

PROFILE_FIELDS = ["Name", "Services", "Business address", "Industries", "Locations", "Email channel"]


def masked(v):
    return f"set ({len(v)} chars)" if v else "missing"


def get(url, headers=None, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()


def check_pagespeed(key):
    q = urllib.parse.urlencode({"url": "https://www.google.com", "strategy": "mobile", "key": key})
    try:
        status, _ = get("https://www.googleapis.com/pagespeedonline/v5/runPagespeed?" + q, timeout=60)
        return "ok" if status == 200 else f"http {status}"
    except urllib.error.HTTPError as e:
        return "invalid key or API not enabled" if e.code in (400, 403) else f"http {e.code}"
    except Exception as e:  # noqa: BLE001
        return f"unreachable ({type(e).__name__})"


def check_agentmail(key):
    try:
        status, body = get("https://api.agentmail.to/v0/inboxes", {"Authorization": f"Bearer {key}"})
        n = len(json.loads(body).get("inboxes", [])) if status == 200 else 0
        return f"ok ({n} inbox{'es' if n != 1 else ''})"
    except urllib.error.HTTPError as e:
        return "invalid key" if e.code in (401, 403) else f"http {e.code}"
    except Exception as e:  # noqa: BLE001
        return f"unreachable ({type(e).__name__})"


def check_profile(path):
    if not os.path.exists(path):
        return {"exists": False, "missing": PROFILE_FIELDS}
    text = open(path, encoding="utf-8").read()
    missing = [f for f in PROFILE_FIELDS
               if not re.search(rf"^{re.escape(f)}:\s*\S", text, re.M)]
    leaked = bool(re.search(r"(AIza[0-9A-Za-z_-]{20,}|sk-[A-Za-z0-9]{20,}|am_[A-Za-z0-9]{16,})", text))
    return {"exists": True, "missing": missing, "possible_secret_in_profile": leaked}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--profile", default="agency-profile.md")
    p.add_argument("--no-network", action="store_true")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    out = {"python": sys.version.split()[0], "keys": {}, "checks": {}}
    for k, label in KEYS.items():
        out["keys"][k] = {"label": label, "status": masked(os.environ.get(k, ""))}
    if not a.no_network:
        if os.environ.get("PAGESPEED_API_KEY"):
            out["checks"]["pagespeed"] = check_pagespeed(os.environ["PAGESPEED_API_KEY"])
        if os.environ.get("AGENTMAIL_API_KEY"):
            out["checks"]["agentmail"] = check_agentmail(os.environ["AGENTMAIL_API_KEY"])
    out["profile"] = check_profile(a.profile)
    out["ready"] = out["profile"]["exists"] and not out["profile"]["missing"]

    if a.json:
        print(json.dumps(out, indent=2))
        return
    print(f"Python {out['python']}")
    for k, v in out["keys"].items():
        print(f"  {k:<20} {v['status']:<16} {v['label']}")
    for k, v in out["checks"].items():
        print(f"  check {k}: {v}")
    pr = out["profile"]
    if not pr["exists"]:
        print("  agency-profile.md: not found, run setup")
    else:
        print(f"  agency-profile.md: missing {', '.join(pr['missing']) or 'nothing'}")
        if pr.get("possible_secret_in_profile"):
            print("  WARNING: profile appears to contain an API key; move it to environment or secrets")
    print("READY" if out["ready"] else "SETUP NEEDED")


if __name__ == "__main__":
    main()