# bfcm-readiness

A portable agent skill that audits WooCommerce stores for Black Friday and Cyber Monday, publishes
a report, then remediates only what a human approves.

Runs unmodified on Hermes and OpenClaw. Nothing in the skill depends on a runtime specific tool,
and both path conventions are declared side by side in SKILL.md.

## Install

```bash
./install.sh              # detects ~/.hermes or ~/.openclaw
./install.sh hermes
./install.sh openclaw
./install.sh --dest /some/skills/root
```

Or place the directory by hand.

| Runtime | Path | Refresh |
| --- | --- | --- |
| Hermes | `~/.hermes/skills/ecommerce/bfcm-readiness/` | New session, or `/reset` |
| OpenClaw | `~/.openclaw/workspace/skills/bfcm-readiness/` or `~/.openclaw/skills/` for all agents | File watcher, else `openclaw gateway restart` |

Verify with `hermes skills list` or `openclaw skills list`. Invoke with `/bfcm-readiness`.

## Layout

```
bfcm-readiness/
├── SKILL.md                      always loaded
├── README.md                     not loaded by the agent
├── install.sh                    not loaded by the agent
├── references/
│   ├── audit-steps.md            Steps 0 to 7
│   ├── freeze-window.md          Step 0
│   ├── data-sources.md           a source is unavailable
│   ├── thresholds.md             scoring a measurement
│   ├── report-template.md        writing the report
│   ├── deliverable.md            publishing the report
│   ├── remediation.md            Step 8
│   └── failure-index.md          a symptom appears during the sale
└── scripts/
    ├── freeze_window.py          optional, Hermes, needs Python
    └── freeze_window.mjs         optional, OpenClaw, needs Node
```

References load on demand, so the skill costs almost nothing until it is used.

## Dependencies

None are hard. The skill degrades instead of failing.

- A hosting platform MCP, Cloudways MCP where the site is on Cloudways. Without it, Step 2 trends
  and the tier recommendation fall to UNKNOWN and the rest continues
- A WordPress MCP per site. Without it, the ladder in `references/data-sources.md` falls through to
  WP CLI over SSH, the REST API, then plain HTTP observation
- A document server for the deliverable. Without one, the report falls back to a markdown file, then
  to chat
- Python 3.7 or later (Hermes) or Node (OpenClaw) for the optional freeze window script. Without it,
  the agent reads the table

## Safety model

Steps 0 to 7 never write. Step 8 writes only under per change human approval, and Class D changes,
anything touching payment credentials, gateway mode, production coupons, orders, refunds or
customer data, are refused outright with a handoff instead. Order data is read as counts and ages
only. Secrets are never read, echoed or logged.
