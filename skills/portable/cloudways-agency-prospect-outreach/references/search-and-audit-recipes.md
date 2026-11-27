# Prospect search and batch audit recipes

## Finding prospects with web search

- Query for the prospect's own about/team/shop page, not for the category. "Shopify ecommerce brand small team about us" returns other Shopify agencies; "small indie game studio website team of 10 developers our games about us", "independent board game publisher small company official site shop", "small creative design studio branding team of 8 portfolio contact" and "boutique animation studio small team showreel contact us" return real businesses.
- Discard results that are directories, press/review sites, marketplaces, Reddit/Facebook threads, email-list vendors, and agencies in the same trade as the user (competitors, not clients). Also discard large brands that fail the size filter.
- Collect ~1.5x the target count, run one search per industry in the profile, then audit all candidates.

## Batch auditing

- The terminal tool refuses commands that use `&` backgrounding. Run audits in parallel from `execute_code` with `concurrent.futures.ThreadPoolExecutor(6)` calling `python3 scripts/site_audit.py https://DOMAIN --json` via `subprocess.run(..., timeout=150, cwd=<skill dir>)`. 18 sites took ~95s.
- The audit script reads `PAGESPEED_API_KEY` from its process environment. `execute_code` does not inherit `~/.hermes/.env`, so parse that file and pass it in `env=`. In the terminal, use `set -a; . ~/.hermes/.env; set +a`. Never print the value.
- Save each result to `~/.hermes/outreach/audits/<domain>.json` and summarise from those files in code (domain, `pagespeed.mobile_performance`, `pagespeed.lcp_s`, `ttfb_s`, `ssl.days_left`, `html.published_emails`, `html.has_form`, and `findings` with severity high/medium).
- stderr contains a harmless DeprecationWarning; ignore it.
- Lab LCP values can be extreme (30s+). In emails say "Google's PageSpeed test measured...", never that real visitors wait that long.
- A site scoring 90+ on PageSpeed has little to pitch even if a minor flag (e.g. missing viewport tag) appears; drop it rather than pad the shortlist.
- `html.published_emails` is the only source of "verified" contacts from the audit. Sites with none need a contact lookup; anything guessed is labelled guessed.

## Gmail via himalaya without exposing the password

Build `~/.config/himalaya/config.toml` in a single shell command that sources `~/.hermes/.env`, strips spaces from `GMAIL_APP_PASSWORD` (`tr -d ' '`; Google displays it in 4-character groups), writes it with a heredoc, and runs `chmod 600`. Never echo the variable. Verify with `~/.local/bin/himalaya mailbox list`.
