---
name: cloudways-lovable-velocity-migrator
description: "Use when deploying Lovable or Node.js apps to Velocity."
version: 1.4.0
author: Cloudways
license: MIT
metadata:
  hermes:
    tags: [cloudways, velocity, nodejs, mcp, deployment, hosting, lovable, migration]
    related_skills: [hermes-agent]
---

# Cloudways Lovable → Velocity Migrator (Velocity Deployments via MCP)

Deploy Node.js applications (including Lovable-built apps) to Cloudways Velocity hosting using the Cloudways MCP server.

## When to Use

- User wants to deploy a Node.js app (Express, Next.js, Vite, TanStack, etc.) to Cloudways Velocity
- User wants to migrate a Lovable-built app to Velocity
- User asks about Cloudways Velocity servers, apps, or deployments
- User wants to manage Velocity environment variables, domains, or staging apps

## Preflight: ask for these four things FIRST

Before any inspect, fork, or deploy step, check all four and ask the user for whatever is missing. Ask in one message (or one `clarify`), not one by one. Never ask the user to paste a token, key, or password in chat.

### 1. Supabase Credentials
- Lovable apps using Supabase will fail to hydrate without these env vars set on Velocity.
- Ask for these 3 values upfront (they're in the repo's `.env` file, but that file isn't used by Velocity):
  - `SUPABASE_URL`
  - `SUPABASE_PUBLISHABLE_KEY`
  - `SUPABASE_PROJECT_ID`
- When setting env vars on Velocity, set both the base and VITE_-prefixed versions (6 total) using the same values. The VITE_ prefix is required for client-side access.
- These are publishable keys (safe to share in chat). Service-role keys are secrets — mark those `is_private: true` if needed.
- **Warn the user**: setting these connects Velocity to the original Lovable Cloud Supabase backend (shared users/data). If they want a separate backend, they need their own Supabase project.

### 2. Lovable Auth
- Goal: reach the user's Lovable projects through the Lovable MCP (`https://mcp.lovable.dev`, OAuth is the documented login; Lovable docs say API-key auth is not available).
- Check whether a Lovable MCP tool is already available (`tool_search` for "lovable"). Lovable is not in the `manage_connections` hosted list or MCP install catalog as of last check, so it usually has to be added as a custom MCP server; the OAuth login happens in the user's browser.
- **If Lovable Auth cannot connect, do not keep retrying. Ask the user to paste the GitHub repo URL** (the Lovable project's synced repo) and continue from there.

### 3. Cloudways MCP
- Check with `mcp__cloudways__list_available_toolsets` (must include `velocity_tools`).
- **If it is not connected, never ask for the access token in chat.** Guide the user to create their API access token using this guide: https://support.cloudways.com/en/articles/5136065-how-to-create-and-manage-cloudways-api-access-tokens

**Steps to create the API access token:**
1. Log in to the Cloudways Platform
2. Go to **Account → API** (or **Settings → API**)
3. Click **Generate API Key**
4. Copy the generated API key (it won't be shown again)

**Steps to connect to your Hermes/OpenClaw agent:**
1. Copy the access token
2. Open the agent
3. Head to **AI Agent** tab
4. Head to **MCP**
5. Head to **Cloudways MCP** section
6. Paste the token
7. Click **Connect**

Then re-check the connection with `mcp__cloudways__list_available_toolsets`.

### 4. GitHub Auth
- **Always ask the user to add the GitHub MCP first.** Try `manage_connections` (`install` with `{"name": "github", "mcp": true}`); GitHub was not in the MCP install catalog last time, so expect this to fail and say so plainly.
- **If the GitHub MCP fails or is unavailable, use the device login method**: `gh auth login --hostname github.com --git-protocol https --web` run with `background=true, notify=true`, show the one-time code and https://github.com/login/device, and wait for the completion notice. Verify with `gh auth status`.
- Approval rules below still apply to every GitHub change.

Only continue once Cloudways MCP, GitHub access, and Supabase credentials (if the app uses Supabase) are ready, and a repo URL is known (from Lovable or pasted by the user).

## Always-on rules (this user)

- **GitHub changes need explicit approval first**: fork, branch, commit, push, PR, and visibility changes (public/private). Ask with `clarify`; if it times out or is unanswered, do NOT proceed — report and wait.
- **Never edit code on main**: create a branch, add tests first, then edit code on that branch. Pushes to the deployed branch trigger auto-deploy, so branch work does not redeploy until merged.
- **Before making a repo public**, offer a read-only secrets scan (filenames, contents, history); public exposes full git history.
- **Confirm price for every new server** (`velocity_plan_activate`); each call creates a new subscription. Check `velocity_server_list` first. Adding an app to an existing server is not an extra charge.
- **Verify a deploy in two steps**: (1) `curl -s -o /dev/null -w "%{http_code}" <app_fqdn>` for 200, then (2) for SSR/React apps load it in a real browser and check console errors. `operation_status` success alone proves nothing: builds succeed while apps 502, and curl returns 200 while the client crashes on hydration.
- **Report what was NOT tested** (login, signup, feature flows) instead of calling the app fully working.
- **Read build logs before guessing at causes** (`velocity_deployment_get` gives the signed log URL; `velocity_deployment_history_list` only has a one-line summary).

## Prerequisites

- Cloudways MCP server connected (check with `mcp__cloudways__list_available_toolsets`); see Preflight for what to do if not
- VCS provider (GitHub/GitLab/Bitbucket) connected to Cloudways account

## Key Concept: Velocity Toolset

Velocity tools are in a **separate toolset** (`velocity_tools`), not the default tool list. You must call them via:

```python
mcp__cloudways__execute_tool(
    toolset="velocity_tools",
    tool_name="velocity_plan_activate",  # NOT "tool" - use "tool_name"
    arguments={...}
)
```

**Pitfall**: The parameter is `tool_name`, not `tool`. Using `tool` returns a missing required argument error.

## Deployment Workflow

### 1. Check VCS Connection
```python
execute_tool(toolset="velocity_tools", tool_name="velocity_vcs_connections_get", arguments={})
```
Confirm the user's Git provider (github/gitlab/bitbucket) shows `connected: true`.

### 2. Get Plan Catalog
```python
execute_tool(toolset="velocity_tools", tool_name="velocity_plans_list", arguments={})
```
Returns: plans (with IDs, pricing), clouds, regions, frameworks, node_versions.

### 3. Inspect the Repository
```python
execute_tool(toolset="velocity_tools", tool_name="velocity_vcs_repo_inspect", arguments={
    "platform": "github",
    "owner": "username",
    "repo": "repo-name"
})
```
Auto-detects: framework, package manager, build commands, Node version.

### 4. Get Namespace ID (REQUIRED)
```python
execute_tool(toolset="velocity_tools", tool_name="velocity_vcs_namespaces_list", arguments={
    "platform": "github"
})
```
Returns namespace `id` for the user/org. **This ID is required for activation.**

### 5. Confirm with User
Velocity plans are **PAID**. Always confirm:
- Plan name and monthly price
- Region
- Repository to deploy

### 6. Activate Plan (Deploy)
```python
execute_tool(toolset="velocity_tools", tool_name="velocity_plan_activate", arguments={
    "plan_id": "1",           # From plans_list
    "cloud": "do",
    "region": "nyc3",
    "repo_full_name": "owner/repo",
    "branch": "main",
    "platform": "github",
    "namespace_id": "123456",  # REQUIRED - from namespaces_list
    "app_label": "my-app",     # REQUIRED
    "server_label": "MyServer",
    "server_storage": 25,      # REQUIRED - in GB
    "framework_id": "11",      # From plans_list frameworks
    "app_mode": "ssr",         # or "csr"
    "build_config": {
        "package_manager": "npm",  # or "bun", "yarn", "pnpm"
        "install_command": "npm install",
        "build_command": "npm run build"
    }
})
```

**Pitfall**: API returns 422 if missing `namespace_id`, `app_label`, or `server_storage` — these are required but not obvious from the schema.

**Pitfall**: `server_id` must be a string, not an integer. Passing `server_id: 1691141` returns `Validation error: server_id: Input should be a valid string`. Always use `server_id: "1691141"`.

**Pitfall**: `server_id` must be a string, not an integer. Passing `server_id: 1691141` returns `Validation error: server_id: Input should be a valid string`. Always use `server_id: "1691141"`.

### 7. Poll Operation Status
```python
mcp__cloudways__operation_status(operation_id="flex-XXXXXXXX")
```
Check `is_completed`: "0" = in progress, "1" = done, "-1" = failed.

## Pitfalls

### Namespace Access Limitation
Repos are linked through the namespaces returned by `velocity_vcs_namespaces_list` — typically the user's personal account and orgs they belong to — and `namespace_id` is required. `velocity_vcs_repo_inspect` can read other orgs' public repos, but deploying them is untested (one attempt failed for an unrelated reason: the target server had been terminated). Default to forking a third-party repo first, with user approval.

### Fork Workflow for External Repos

When user wants to deploy a repo from an org they don't have access to:

1. **Authenticate GitHub** (if not already): follow Preflight step 3 (GitHub MCP first, device login as fallback). CLI device login:
   ```bash
   # Must run in background - times out in foreground
   terminal(command="gh auth login --hostname github.com --git-protocol https --web", background=true, notify=true)
   ```
   User gets a device code to enter at https://github.com/login/device

2. **Fork the repo**:
   ```bash
   gh repo fork <org>/<repo> --clone=false
   ```

3. **Verify fork exists**:
   ```bash
   gh repo view <user>/<repo> --json name,url
   ```

4. **Deploy from the fork** using `velocity_plan_activate` with the user's namespace_id and forked repo name.

**Pitfall**: `gh auth login --web` times out if run in foreground mode (even with 300s timeout) because it waits for the OAuth callback. Always use `background=true, notify=true` so the process survives while the user completes browser auth.

**gh / git / tool gotchas**:
- `gh repo edit --visibility public` has no `--accept-visibility-change-consequences` flag in this gh version; use `--visibility public` alone, after approval.
- `git push` fails with `could not read Username` until `gh auth setup-git` runs.
- `git commit` needs a local identity: ask the user for name and email instead of inventing one.
- `write_file` and `patch` are blocked outside `~/.hermes` (HERMES_WRITE_SAFE_ROOT); edit cloned repos through `terminal`.
- Builds take 2-4 minutes. A long foreground `terminal` call can time out, so poll with separate short `sleep` calls and `operation_status`.

### Lovable / TanStack apps fail to start (502)
Lovable's `@lovable.dev/vite-tanstack-config` builds for Cloudflare Workers by default. The build succeeds but the app does not start on Velocity (Node). A likely fix is `nitro: { preset: "node-server" }` in `vite.config.ts` with start command `node .output/server/index.mjs`. Verified to work. Propose it on a branch, then follow the playbook below and verify with curl plus a browser load.

### npm install crashes on Node 22 (`reading 'edgesOut'`)
Velocity's default Node 22 ships npm 10.9.9, which crashes on repos with `overrides` and no npm lockfile (e.g. bun-based Lovable apps). Fix: set `node_runtime_version_id: 1` (Node 24) via `velocity_build_config_update` with `deploy=true`; no GitHub change needed. Confirmed in the signed build log from `velocity_deployment_get`.

**Pitfall**: `node_runtime_version_id` must be INSIDE the `build_config` object, not a top-level argument. Passing it top-level silently fails — the response shows `node_runtime_version_id: null` and the build runs on the old Node version. Correct call:
```python
velocity_build_config_update(server_id="...", app_id="...", deploy=true, build_config={
    "package_manager": "npm",
    "install_command": "npm install",
    "build_command": "npm run build",
    "start_command": "node .output/server/index.mjs",
    "node_runtime_version_id": 1  # MUST be inside build_config
})
```

**Pitfall**: `node_runtime_version_id` must be INSIDE the `build_config` object, not a top-level argument. Passing it top-level silently fails — the response shows `node_runtime_version_id: null` and the build runs on the old Node version. Correct call:
```python
velocity_build_config_update(server_id="...", app_id="...", deploy=true, build_config={
    "package_manager": "npm",
    "install_command": "npm install",
    "build_command": "npm run build",
    "start_command": "node .output/server/index.mjs",
    "node_runtime_version_id": 1  # MUST be inside build_config
})
```

### Lovable app migration playbook (verified end to end)
0. **Preflight**: Lovable Auth, Cloudways MCP, GitHub Auth (see the Preflight section; paste-the-repo fallback if Lovable fails).
1. **Inspect (read-only)**: `velocity_vcs_repo_inspect`, `velocity_server_list` (check `app_count` vs `allowed_apps`), and read the repo's `vite.config.ts` / `package.json`.
2. **Ask approval in one `clarify` call**: the fork, target server (existing server = no extra cost; new server = confirm price), and the Node preset fix.
3. **Fork and branch**: `gh repo fork <org>/<repo> --clone=false`, `gh repo clone <user>/<repo>`, `git checkout -b fix/velocity-node-preset`.
4. **Red**: add a vitest test asserting `vite.config.ts` contains `nitro: { preset: "node-server" }`; run it and confirm it fails.
5. **Green**: add `nitro: { preset: "node-server" }` to `defineConfig(...)`; run the full test suite and `npm run build`; confirm `.output/server/index.mjs` exists; boot it with `PORT=3911 node .output/server/index.mjs` and curl 200.
6. **Commit only the config and the test**. Do not commit npm's generated `package-lock.json` into a bun repo. Show the diff, get approval, run `gh auth setup-git`, then `git push -u origin <branch>`.
7. **Deploy**: `velocity_app_create` with `branch=<fix branch>`, `framework_id=11`, `app_mode=ssr`, npm commands, `start_command=node .output/server/index.mjs`. If install fails with `edgesOut`, set Node 24 (`node_runtime_version_id: 1`) via `velocity_build_config_update deploy=true`. (`velocity_app_create` also accepts `node_runtime_version_id`; passing it up front is untested.)
8. **Env vars**: if the app uses Supabase, set SUPABASE_* and VITE_SUPABASE_* (see the hydration pitfall below; approval and shared-backend warning first), then redeploy.
9. **Verify**: curl 200, then browser-load `/` and `/auth` with console hooks; expect zero errors. Build log should show `preset: node-server` and `SSR application started with PM2`.
10. **After**: auto-deploy follows the deployed branch, so a push redeploys; repoint the app to `main` after the user merges.

### Page loads then shows "This page didn't load" (Lovable + Supabase)
Server returns 200 with real HTML, but the client crashes on hydration: console says `Missing Supabase environment variable(s): SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY`. `curl` cannot see this. Check with a real browser (install `Page.addScriptToEvaluateOnNewDocument` console.error/unhandledrejection hooks, then reload). The repo's committed `.env` is not used by Velocity. Fix (Cloudways only): `velocity_env_vars_upsert` for SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY, SUPABASE_PROJECT_ID and the VITE_-prefixed copies, then redeploy (`velocity_build_config_update deploy=true`) so VITE_ values bake into the client build. Warn the user this shares the original author's Lovable Cloud backend (users/data) unless they set up their own Supabase; get approval first. Publishable keys are not secrets; service-role keys are, so mark those is_private.

**Pitfall**: The parameter name is `env_variables`, not `variables`. Using `variables` returns `Validation error: env_variables: Field required`.

### Adding Apps to Existing Servers
Use `velocity_app_create` to add another app to an existing Velocity server (no new plan/billing). Use `velocity_plan_activate` only when creating a new server. Each plan limits the number of apps per server (`allowed_apps` in plans_list; `app_count` in `velocity_server_list`).

Working call (static Vite app): `server_id`, `repo_full_name`, `branch`, `platform="github"`, `namespace_id`, `app_label` (the user-requested name, spaces allowed), `framework_id` (10 = Vite CSR), `app_mode="csr"`, `build_config={package_manager, install_command, build_command, publish_directory:"dist"}`. It returns `operation_id` (install) and `build_operation_id` (build); poll both. Get `app_fqdn` from `velocity_app_overview_get`.

Use the package manager that matches the repo's lockfile as reported by `velocity_vcs_repo_inspect`, but if install fails with bun, fall back to npm.

### service_restart for PM2
`service_restart` with `product="velocity"`, `service="pm2-node-app"` needs `sys_user`, which is the app's `sys_user` (returned by `velocity_app_create`), not the Postgres user. Do not assume a restart fixed anything; re-check with curl.

## Common Framework IDs

| ID | Framework | Mode |
|----|-----------|------|
| 1 | Express | SSR |
| 3 | React | CSR |
| 5 | Astro SSR | SSR |
| 6 | Astro CSR | CSR |
| 7 | Next.js SSR | SSR |
| 8 | Next.js CSR | CSR |
| 10 | Vite CSR | CSR |
| 11 | TanStack SSR | SSR |

## Discovering Available Tools

List all Velocity tools:
```python
mcp__cloudways__get_toolset_tools(toolset="velocity_tools")
```

43 tools covering: server management, app lifecycle, staging, deployments, Supabase integration, VCS operations, env variables, and domains.

