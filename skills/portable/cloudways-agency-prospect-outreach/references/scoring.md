# Qualification and scoring

## Hard filters (fail any one and the prospect is dropped)

- Outside the profile's target industries or locations
- Already in `prospects-log.csv`, an existing client, or on the do-not-contact list
- No working website, parked domain, or a page that is only a social media link
- Clearly too large (national chain, in-house web team) or too small for the agency's price range
- Matches a "Learned exclusion" in the profile

## Score out of 100 (default weights, editable in the profile)

|| Factor | Weight | Full points | Partial | Zero |
||---|---|---|---|---|
|| Need | 40 | Three or more serious audit issues (not secure, expired SSL, no mobile, PageSpeed under 50, CMS several years old) | One or two serious, or several minor | Site is modern and fast |
|| Fit | 25 | Industry the agency has done before, ideal size, in target area | Adjacent industry or edge of area | Weak match |
|| Ability to pay | 15 | Multiple locations, active ads, hiring, premium services, recent funding | Established single location | Signs of very low budget |
|| Reachability | 10 | Named decision maker with verified email | Generic info@ address | Contact form only |
|| Timing | 10 | New location, rebrand, new leadership, recently hiring, or copyright year 3+ years old | One weak signal | None |

Need gets the most weight because the email depends on it: without real problems there is nothing specific to say.

## Bands

- 70 and above: shortlist and draft
- 50 to 69: hold, log, no draft
- below 50: drop and log

Show the score breakdown in the report so the user can see why each prospect made the list.

## Merged data (user prefers raw data tables, no numeric grading)

- Present audit-script checks and PageSpeed mobile+desktop metrics merged in two plain tables. Do not add scores, bands or rankings unless asked.
- Use BOTH the audit JSON and PageSpeed mobile+desktop runs. Run PageSpeed via the API (strategy=mobile and desktop) and keep FCP, LCP, TBT, CLS and Speed Index, not just the score.
- Lab scores swing 10-20 points between runs. Average the audit-script run and the API run, report the spread, and mark confidence low when it is 15+. Never quote a single extreme number (e.g. a 41s LCP) as fact.
- Data-quality gate: if the audit got a non-200 status or a page under 1KB (bot wall, HTTP 202), exclude all HTML findings (viewport, title, meta, forms) for that site. Only PageSpeed data is trustworthy then.
- Do not give pay and timing a high value without evidence; use 0.5 and say so. Reach: named verified 1.0, generic verified 0.6, unverified 0.3, none or form only 0.
- Score before drafting. Do not draft for prospects below the shortlist band without telling the user.