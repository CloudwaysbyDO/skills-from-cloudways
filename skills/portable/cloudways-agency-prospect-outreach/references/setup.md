# Upfront setup

Collect everything the run needs **before** any research, audit or drafting. Finding out halfway through that Gmail is not connected or a key is missing wastes the agency's tokens and patience.

## How to run setup

**Run as a gated wizard.** Each section is a gate — complete one before moving to the next. Use the `clarify` tool for each gate, not inline chat text.

1. **Check what already exists first.** Run `python scripts/check_setup.py` (it reads environment variables and `agency-profile.md`, and never prints secret values).

2. **Offer to pre-fill from existing materials.** Before asking setup questions, use `clarify` to offer:
   ```
   Before we start, I can save you time by pulling details from what you already have:
   
   - Share your agency website URL (I'll extract name, services, team, address, past work)
   - Or upload a document (pitch deck, about page, proposal PDF)
   - Or skip and answer questions manually
   ```
   
   **If they share a website URL:**
   - Fetch the homepage, about page, services page, contact page
   - Extract: agency name, services offered, team members, business address, testimonials, case studies, past clients
   - Pre-fill these into the profile
   
   **If they upload a document:**
   - Read the PDF/document
   - Extract the same fields
   - Pre-fill into the profile
   
   Then only ask about fields that are still missing in each gate.

3. **Show the user what's coming:**
   > I'll walk you through setup in 4 steps:
   > A. About your agency
   > B. What kind of clients you want
   > C. Email channel for drafts
   > D. API keys (optional)
4. **Proceed through each gate** using `clarify` prompts. Skip questions you already have answers for from the website/document. Wait for answers before moving to the next gate.
5. **Confirm before starting.** Summarize the setup in five lines and ask "Ready to start?" Only then move to prospecting.

On later runs, if `agency-profile.md` exists and `check_setup.py` passes, show the five line summary and ask "Still accurate?" instead of repeating setup.

## Gate A. About your agency

Ask only what's missing (some may be pre-filled from website/document) via `clarify`:

1. Agency name and website (if any)
2. Services you offer — WordPress, Shopify, redesigns, speed optimization, SEO, care plans, branding?
3. Typical project price range — e.g. £2k-10k, or monthly retainers
4. A past project with a result (optional but helps emails convert) — e.g. "cut load time from 6s to 1.5s for a dental clinic"
5. Your name and role for the email signature
6. Business address — required for CAN-SPAM/GDPR compliance in cold emails

If you pre-filled some fields, show them: "I found these from your website — confirm or edit:"

## Gate B. What kind of clients you want

Ask only what's missing via `clarify`:

1. Target industries — and which you've worked in before
2. Locations — specific city/region, or anywhere?
3. Ideal client size — solo practitioners, 5-50 staff, multi-location?
4. Who to avoid — tiny budgets, specific industries, existing clients?
5. Prospect source — will you give me a list of domains, or should I search for prospects, or both?
6. How many prospects per run? (default: 10)

If past clients or industries were found on their website, pre-fill: "I saw you've worked with dentists and law firms — target similar?"

## Gate C. Email channel for drafts

Ask via `clarify` as a single-select with these choices:

|| Option | What is needed | Notes |
||---|---|---|
|| Gmail / Google Workspace | OAuth connection or `gws` CLI | Sends from agency's real domain with existing reputation |
|| Outlook / Microsoft 365 | Connected Outlook or Microsoft Graph tool | Drafts go to the Drafts folder |
|| Other IMAP mailbox | IMAP host, username, app password stored as secrets | Drafts saved to IMAP Drafts folder |
|| None for now | Nothing | Drafts saved to `outreach-drafts.md` or CSV |

**After selection: Connect AND verify before proceeding to Gate D.**

1. If Gmail: Run OAuth flow, then verify by listing labels or fetching profile
2. If Outlook: Connect, then verify by listing folders
3. If IMAP: Test connection with credentials
4. If None: Confirm user accepts file fallback

**Do not proceed to Gate D or any audit work until the email channel is confirmed working.** If connection fails twice, offer file fallback and get explicit confirmation.

## Gate D. API keys (PageSpeed is required; see SKILL.md hard requirements)

Ask via `clarify`:

|| Key | Used for | Required? | How to get it |
||---|---|---|---|
|| Google PageSpeed API key (`PAGESPEED_API_KEY`) | Mobile speed scores — the strongest pitch evidence | Recommended. Works without a key at very low volume | Free from Google Cloud Console: create a project, enable PageSpeed Insights API, create an API key |

**Note:** No other keys are required. Web search, browser, and auditing all work without additional API keys.

Optional integrations (ask only if user mentions them):
- Enrichment (`HUNTER_API_KEY`, `APOLLO_API_KEY`) — for verified decision maker emails
- CRM (HubSpot, Pipedrive) — for logging shortlisted prospects

## Handling secrets

- Ask the user to add keys to the agent's **secrets or environment settings** (on Cloudways, the agent dashboard or terminal), not to paste them into chat. If they paste one anyway, store it as an environment variable or in the agent's secret store, never in `agency-profile.md`, the report, logs or memory, and do not repeat it back.
- In `agency-profile.md`, record only which integrations are configured (for example "PageSpeed: configured"), never the value.
- Verify each key with one cheap call through `check_setup.py`. If a check fails twice, mark that integration "unavailable", tell the user in one sentence, and continue with the fallback rather than retrying.

## Save as agency-profile.md

```markdown
# Agency profile
Updated: YYYY-MM-DD

## Agency
Name:
Website:
Services:
Price range:
Proof:
- Project, result

## Sender
Name:
Role:
Signature:
Business address:

## Targets
Industries:
Locations:
Client size:
Avoid / do not contact:
Prospect source: my list | agent search | both
Prospects per run: 10
Shortlist threshold: 70
Score weights: need 40, fit 25, pay 15, reach 10, timing 10

## Channels
Email channel: AgentMail | AgentMail MCP | AgentMail API | Gmail | Outlook | IMAP | none
Mailbox or inbox:
Approval channel:

## Integrations (status only, never keys)
PageSpeed: configured | not configured
Web search: built-in | key configured | not available
Browser: available | not available
Enrichment: Hunter | Apollo | none
CRM: HubSpot | Pipedrive | CSV

## Learned exclusions
```