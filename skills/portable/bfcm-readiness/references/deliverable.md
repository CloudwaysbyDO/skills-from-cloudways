# Deliverable

Build the full report first against `references/report-template.md`, then publish. Never draft directly
into the document.

The target is whichever document server the runtime has connected. Check what is actually available
before choosing, do not assume. The ladder below sets the preference order.

## Publishing to Google Drive

Where a Drive server is connected, create the document with `create_file`, passing the finished
report as `textContent` with `contentMimeType` set to `text/markdown`. Drive converts it to a native
Google Doc, which keeps headings and tables. If a table renders badly, republish the same content
as `text/html` instead. Do not set `disableConversionToGoogleType`, that would leave a plain file
rather than a doc.

## Publishing elsewhere

Confluence, Notion or any other connected wiki server takes the same finished markdown. Use its
create page call, keep the same title convention, and return the page link.

Return the link in chat with a three line summary, the verdict, the P0 count, and the single thing to do
first. The link is the deliverable, not a retelling of the report.

## Naming

```
BFCM Readiness [client or fleet name] [YYYY-MM-DD]
```

Add `Remediation` as a suffix when the document covers a Step 8 run rather than an audit.

## Versioning

On Drive, `update_file` changes title and location only, not content. There is no in place content
edit, so every re run produces a new document. Treat any document server the same way unless it
genuinely supports content update.

- Create a new document per run, never overwrite
- Put a Previous run line under the header with the date and link to the prior document
- Put a Changes since last run table directly after the verdict, listing findings closed, findings new,
  and findings unchanged. On a re run this table is the first thing anyone reads
- Keep all runs in one folder per client so the sequence is visible

## Placement

Ask once where the document should live, and offer the sensible default of a folder named for the
client or the fleet. Search for an existing folder before creating one. Reuse the same folder for every
later run without asking again.

## Sharing

Sharing is a separate action and needs explicit approval naming the recipient and the role. Never
share on your own initiative, never guess a recipient, and never widen access beyond what the user
asked for. Default to commenter when the user names a person but not a role, since a readiness
report attracts comments and rarely needs co editing.

## Fallback ladder

| Rank | Method |
| --- | --- |
| 1 | Google Doc via a connected Drive server |
| 2 | Another connected document or wiki server, Confluence or Notion for example |
| 3 | A markdown file in the working folder, presented to the user |
| 4 | The report inline in chat |

Say which was used and why. A report delivered as a markdown file is still a complete deliverable, so
do not stop or ask for a document connection before falling back.

## Fleet runs

One document per fleet, not one per site, with the per site verdict table at the top and a section per
site below. A separate document per site fragments the thing the agency actually needs, which is the
rollup. Split only when the user asks, or when sites belong to different end clients who should not
see each other's data.

## What does not go in the document

Everything in the safety rules still applies to the published artefact, and a document is easier to
forward than a chat message.

- No secrets, keys, tokens or credentials of any kind
- No customer names, addresses, emails, order contents or transaction identifiers
- No raw tool output pasted wholesale
- No server IP addresses or SSH details beyond what the client already has

A readiness document gets shared with people who were never in the audit conversation. Write it so
that is safe.
