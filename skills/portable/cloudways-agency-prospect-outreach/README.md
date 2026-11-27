# Agency Prospect Outreach

Automated web agency lead generation: audit prospects' sites and generate personalized outreach emails.

## Overview

This agent skill, for [Hermes Agent](https://hermes-agent.nousresearch.com/) and [OpenClaw](https://openclaw.ai/), helps any web agency generate qualified leads through:

1. **Automated Website Audits** - Scan prospect sites for real issues:
   - Core Web Vitals performance problems
   - Mobile-friendliness issues
   - Security vulnerabilities
   - SEO problems
   - Accessibility gaps

2. **Personalized Email Generation** - Create custom outreach emails that cite specific findings from each audit

3. **Safe Gmail Integration** - Save drafts to Gmail for review before sending (never auto-sends)

## What's Included

- **SKILL.md** - Main skill documentation and workflow
- **scripts/** - Python automation tools:
  - `site_audit.py` - Website auditing engine
  - `score_prospect.py` - Lead scoring system
  - `check_setup.py` - Setup verification
- **references/** - Detailed guides:
  - `audit-checklist.md` - What to check on each site
  - `email-guidelines.md` - Email best practices
  - `email-channels.md` - Delivery methods
  - `scoring.md` - Lead qualification rules
  - `setup.md` - Initial setup instructions

## Installation

Works with Hermes Agent and OpenClaw (both load `SKILL.md`-style skill folders).

**Option A: Cloudways platform.** Download the skill from the Skills section of the Cloudways platform.

**Option B: manual install.**

1. Download or clone this repository into a folder named `agency-prospect-outreach`
2. Copy it to your agent's skills directory:
   - **Hermes Agent:** `~/.hermes/skills/`
   - **OpenClaw:** `~/.openclaw/skills/` (or your workspace's `skills/` folder)
3. Start a new session and ask for more agency clients. The agent loads the skill itself.

Note: the docs reference `~/.hermes/` paths for the agency profile and logs. On OpenClaw, use an equivalent folder such as `~/.openclaw/`.

## Usage

Once loaded in your agent:

1. **Initial Setup**: The skill will guide you through:
   - Configuring your agency info (name, services, pricing)
   - Setting up Gmail integration
   - Defining your ideal client profile

2. **Generate Leads**: Provide a list of prospect websites and the skill will:
   - Audit each site automatically
   - Score prospects by fit and opportunity
   - Generate personalized outreach emails
   - Save drafts to your Gmail

3. **Review & Send**: Review each draft in Gmail, make any tweaks, then send

## Example Output

Each email includes:
- Personalized greeting using their company name
- 3-5 specific issues found on their site
- Clear value proposition (how you can fix them)
- Soft call-to-action

## Requirements

- Hermes Agent or OpenClaw
- Gmail account (for draft delivery) with a Gmail App Password ([create one](https://myaccount.google.com/apppasswords); requires 2-step verification)
- Google PageSpeed Insights API key ([get one free](https://console.cloud.google.com/apis/credentials); enable the PageSpeed Insights API first)
- Python 3.8+ (included with the agent)

Store the App Password and API key as environment variables or secrets (for example `GMAIL_APP_PASSWORD` and `PAGESPEED_API_KEY`), never in chat or in files you commit.

## Author

Cloudways

## License

MIT License - Free to use and modify
