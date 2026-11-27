# Email channels

The skill only ever creates **drafts**. Verify the chosen channel during setup with one harmless call. If the check fails twice, stop, tell the user what failed in one sentence, and use the local fallback file.

Do not install or authenticate a new integration in the middle of a run. If the chosen channel is not connected, point the user to the agent's integration settings and fall back.

## AgentMail (bundled)

Cloudways Hermes plans include AgentMail, giving the agent its own inbox. Use the built-in AgentMail tool or skill.

- Check: list inboxes, and confirm with the user which inbox is the sender.
- Create the message as a draft in that inbox.
- A brand new inbox domain has no sending reputation. Tell the user to warm it up (a few manual sends a day for a week or two) before sending a batch, or pitches will land in spam.

## AgentMail MCP

If an AgentMail MCP server is connected, use its tools. Check: list inboxes. Confirm it exposes a create draft action; if it only offers send, do not use it for this skill and fall back.

## AgentMail API

Used when no tool or MCP exists, with `AGENTMAIL_API_KEY` from the environment. `check_setup.py` lists inboxes to confirm the key works. Create drafts in the chosen inbox through the API. If drafts are not supported by the installed version, do not send; use the fallback.

## Gmail / Google Workspace

Two setup paths exist — offer both and let the user choose:

| Path | Setup time | Requires | Best for |
|------|------------|----------|----------|
| **himalaya + App Password** | ~2 min | 2FA enabled, App Password | Email-only (drafts in Gmail) |
| **google-workspace OAuth** | ~10 min | Google Cloud project, OAuth consent | Full Workspace (Calendar, Drive, Sheets too) |

If the user only needs email, recommend the himalaya path — it's faster and avoids Google Cloud Console.

### himalaya + Gmail App Password (recommended for email-only)

**Always collect BOTH Gmail address AND App Password together before configuring.**

1. **Install himalaya CLI** (if not present):
   ```bash
   curl -sSL https://raw.githubusercontent.com/pimalaya/himalaya/master/install.sh | PREFIX=~/.local sh
   ```

2. **User creates an App Password** at https://myaccount.google.com/apppasswords
   - Requires 2-Step Verification enabled
   - Select "Other (Custom name)" → type "Hermes" → Generate
   - Copy the 16-character password (looks like `xxxx xxxx xxxx xxxx`)

3. **Configure himalaya v2** at `~/.config/himalaya/config.toml`:

   **IMPORTANT: Use v2 format below. The old v1 format (`backend.type`, `backend.host`, etc.) does NOT work with himalaya 2.x.**

   ```toml
   [accounts.gmail]
   email = "user@gmail.com"
   display-name = "Agency Name"
   default = true

   imap.server = "imaps://imap.gmail.com:993"
   imap.sasl.plain.username = "user@gmail.com"
   imap.sasl.plain.password.raw = "xxxx xxxx xxxx xxxx"

   smtp.server = "smtps://smtp.gmail.com:465"
   smtp.sasl.plain.username = "user@gmail.com"
   smtp.sasl.plain.password.raw = "xxxx xxxx xxxx xxxx"

   mailbox.alias.inbox = "INBOX"
   mailbox.alias.sent = "[Gmail]/Sent Mail"
   mailbox.alias.drafts = "[Gmail]/Drafts"
   mailbox.alias.trash = "[Gmail]/Bin"
   ```

   Note: Gmail uses `[Gmail]/Bin` for trash, not `[Gmail]/Trash`.

4. **Verify**: `~/.local/bin/himalaya mailbox list` should show INBOX, Drafts, etc.

5. **Create drafts** by piping email content to himalaya:
   ```bash
   cat << 'EOF' | ~/.local/bin/himalaya message add --mailbox "[Gmail]/Drafts"
   From: sender@gmail.com
   To: recipient@example.com
   Subject: Your website

   Body text here.
   EOF
   ```

### google-workspace OAuth (for full Workspace access)

Use this path when the user also needs Calendar, Drive, or Sheets. Load the `google-workspace` skill and follow its setup.

- Check: list labels or fetch the profile.
- Ask which Google account the drafts go to.
- Add a `Prospects` label if labels are supported, so drafts are easy to find.
- Benefit: sends from the agency's real domain, which already has reputation.

### Gmail OAuth setup (manual fallback)

If no Gmail integration is connected, guide the user through OAuth:

1. **Create OAuth credentials** in Google Cloud Console:
   - https://console.cloud.google.com/apis/library/gmail.googleapis.com → Enable Gmail API
   - https://console.cloud.google.com/apis/credentials → Create Credentials → OAuth 2.0 Client ID → Desktop app
   - Download the JSON file

2. **Add test user** (required for unverified apps):
   - https://console.cloud.google.com/auth/audience → Add Users → enter their Gmail
   - Without this, OAuth returns "access_denied: The developer hasn't given you access"

3. **User provides the JSON file** → save to `~/.hermes/google_client_secret.json`

4. **Generate auth URL with PKCE**, save state/verifier to `~/.hermes/google_oauth_pending.json`, user opens URL and pastes redirect URL containing the code

5. **Exchange code for tokens** via POST to `https://oauth2.googleapis.com/token`, save to `~/.hermes/google_token.json`

6. **Verify** by calling `GET https://gmail.googleapis.com/gmail/v1/users/me/profile` with Bearer token

### Creating Gmail drafts via raw API

When google-auth Python libraries fail (cffi/cryptography issues), use urllib directly:

```python
import json, base64, urllib.request
from email.mime.text import MIMEText

with open('~/.hermes/google_token.json') as f:
    token = json.load(f)

msg = MIMEText(body, 'plain')
msg['To'], msg['Subject'], msg['From'] = to_email, subject, from_email
raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

req = urllib.request.Request(
    'https://gmail.googleapis.com/gmail/v1/users/me/drafts',
    data=json.dumps({'message': {'raw': raw}}).encode(),
    method='POST'
)
req.add_header('Authorization', f"Bearer {token['access_token']}")
req.add_header('Content-Type', 'application/json')
with urllib.request.urlopen(req) as resp:
    draft = json.loads(resp.read().decode())
```

## Outlook / Microsoft 365

Use a connected Outlook, Microsoft Graph tool or MCP. Check: list mail folders. Create messages in the Drafts folder.

## Other mailbox (IMAP)

For any other provider, use IMAP with host, username and an app password stored as secrets. Save each draft into the Drafts folder with IMAP APPEND and the `\Draft` flag. Never use SMTP in this skill, because SMTP sends immediately.

## Fallback: outreach-drafts.md

Always write every approved draft here too, so nothing is lost if a channel breaks:

```markdown
## 1. Business name (score 82)
To: name@domain.com (verified)
Subject: ...

Body...
```