# managed-agent-skills

Skills we maintain for the OpenClaw and Hermes agent runtimes.

## Layout

```
skills/
├── portable/<name>/     works on both runtimes
├── openclaw/<name>/     OpenClaw only
└── hermes/<name>/       Hermes only
```

Each skill directory looks like this:

```
<name>/
├── SKILL.md          required, loaded by the agent
├── references/       optional, loaded on demand
├── scripts/          optional, helpers for runtimes with a shell
├── README.md         optional, for humans, not loaded by the agent
└── install.sh        optional, per-skill installer
```

The directory name matches `name:` in the `SKILL.md` frontmatter.

## Skills

**[cloudways-agency-prospect-outreach](skills/portable/cloudways-agency-prospect-outreach/)** (portable)
Turns "I want more clients" into a short list of qualified businesses, each with a site audit and a personalized cold email waiting as a draft in the agency's Gmail. After a one time setup, it finds prospects, audits their websites for real issues such as speed, security and outdated tech, and scores them. It then finds the right contact and writes a short pitch based only on what the audit measured. Drafts are never sent, so a human reviews each one. Prospect pages are treated as untrusted data, and every prospect is logged so nobody is pitched twice.

**[cloudways-bfcm-readiness](skills/portable/cloudways-bfcm-readiness/)** (portable)
BFCM Readiness audits WooCommerce stores ahead of Black Friday and Cyber Monday, giving each a READY to BLOCKED verdict with severity-ranked issues and fix by dates tied to the freeze window.

**[cloudways-fleet-performance-checker](skills/portable/cloudways-fleet-performance-checker/)** (portable)
Fleet Performance Checker audits every WordPress or Magento app on a Cloudways account for server, PHP, database, security and PageSpeed issues, then delivers a prioritised action plan.

**[cloudways-lovable-velocity-migrator](skills/portable/cloudways-lovable-velocity-migrator/)** (portable)
Deploys Lovable and Node.js apps to Cloudways Velocity through the Cloudways MCP. It checks prerequisites first, forks and fixes the repo on a branch with your approval, and confirms pricing before creating a server. It then sets environment variables and verifies the live app with curl and a browser load.

**[cloudways-prompt-injection-hardening](skills/portable/cloudways-prompt-injection-hardening/)** (portable)
Keeps untrusted text such as tickets, emails, web pages and logs from steering an agent's tools. That content is treated as data to quote or summarise, never as orders. Privileged actions like merges, credential changes and server settings come only from the operator's trusted channel.

**[cloudways-vulnerability-guardian](skills/portable/cloudways-vulnerability-guardian/)** (portable)
Vulnerability Guardian monitors for critical PHP and WordPress CVEs, checks patch safety across every app on the server, then backs up and updates PHP only after you type an exact confirmation, with health checks and restore on failure.

## Adding a skill

1. Create `skills/<scope>/<skill-name>/SKILL.md`, where scope is `portable`, `openclaw` or `hermes`.
2. Add a row to the table above.
3. Set `version:` in the frontmatter and run `python3 scripts/gen_versions.py`.

## Versioning

A skill's version is the `version:` field (`X.Y.Z`) in its `SKILL.md`. `versions.json` at the repo
root is generated from those files. It lists each skill's version, path and a sha256 per file, plus
the file hashes of recent previous versions. Servers use it to find new versions and to check
whether installed files were edited since the last update. Do not edit it by hand.

After changing a skill:

1. Bump `version:` in its `SKILL.md`.
2. Run `python3 scripts/gen_versions.py`.
3. Commit `versions.json` with the change.

`python3 scripts/gen_versions.py --check` exits 1 if `versions.json` is out of date.

Bump rules:

| Bump | When |
| --- | --- |
| Patch | Wording fixes, threshold tweaks that do not change behavior |
| Minor | A new step, reference or capability |
| Major | A change to the safety model, output contract or step gates |
