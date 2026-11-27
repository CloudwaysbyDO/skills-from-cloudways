#!/usr/bin/env python3
"""Score a prospect out of 100 from a site_audit.py JSON plus agent judgments.

Need is computed from the audit. Fit, pay, reach and timing are judgment calls
the agent makes from its research, passed in as 0.0 to 1.0.

Usage:
    python score_prospect.py audit.json --fit 0.8 --pay 0.5 --reach 1 --timing 0.5 [--profile agency-profile.md]
"""
import argparse
import json
import re

DEFAULT_WEIGHTS = {"need": 40, "fit": 25, "pay": 15, "reach": 10, "timing": 10}
DEFAULT_THRESHOLD = 70


def load_profile(path):
    weights, threshold = dict(DEFAULT_WEIGHTS), DEFAULT_THRESHOLD
    if not path:
        return weights, threshold
    try:
        text = open(path, encoding="utf-8").read()
    except OSError:
        return weights, threshold
    m = re.search(r"Score weights:\s*(.+)", text)
    if m:
        for k, v in re.findall(r"(need|fit|pay|reach|timing)\s*(\d+)", m.group(1), re.I):
            weights[k.lower()] = int(v)
    m = re.search(r"Shortlist threshold:\s*(\d+)", text)
    if m:
        threshold = int(m.group(1))
    return weights, threshold


def need_ratio(audit):
    c = audit.get("severity_counts") or {}
    points = 3 * c.get("high", 0) + 1.5 * c.get("medium", 0) + 0.5 * c.get("low", 0)
    return min(points / 9.0, 1.0)  # three high-severity issues = full need


def main():
    p = argparse.ArgumentParser()
    p.add_argument("audit_json")
    for k in ("fit", "pay", "reach", "timing"):
        p.add_argument(f"--{k}", type=float, default=0.5)
    p.add_argument("--profile")
    a = p.parse_args()

    audit = json.load(open(a.audit_json, encoding="utf-8"))
    weights, threshold = load_profile(a.profile)
    ratios = {"need": need_ratio(audit), "fit": a.fit, "pay": a.pay, "reach": a.reach, "timing": a.timing}
    total_w = sum(weights.values()) or 100
    breakdown = {k: round(weights[k] * max(0, min(1, ratios[k])) * 100 / total_w, 1) for k in weights}
    score = round(sum(breakdown.values()))
    band = "shortlist" if score >= threshold else "hold" if score >= 50 else "drop"
    if not audit.get("reachable", True):
        score, band = 0, "drop"
    print(json.dumps({"domain": audit.get("domain"), "score": score, "band": band,
                      "breakdown": breakdown, "threshold": threshold}, indent=2))


if __name__ == "__main__":
    main()