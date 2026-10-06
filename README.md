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

| Skill | Scope | Purpose |
| --- | --- | --- |
| [bfcm-readiness](skills/portable/bfcm-readiness/) | portable | Audit WooCommerce stores for Black Friday and Cyber Monday, report, remediate with human approval |

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
