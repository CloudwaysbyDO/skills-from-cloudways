# Data sources and fallbacks

Default assumption is a hosting platform MCP, Cloudways MCP where the site is on Cloudways, plus
WordPress MCP. When one is absent or a specific call fails, work down the ladder rather than
stopping.

Tool names vary by MCP version and by host. At the start of a run, list what each connected server
actually exposes and bind capabilities to real names. Never call a guessed tool name.

## Ladder

Try in order. Stop at the first method that returns the value. Record which method was used,
because fidelity differs and the report has to say so.

| Rank | Method | Notes |
| --- | --- | --- |
| 1 | Hosting platform MCP or WordPress MCP | Default. Everything below is a fallback |
| 2 | Another connected MCP covering the same capability | A WooCommerce, analytics or monitoring server may hold the value |
| 3 | WP CLI over SSH | Read subcommands only during Steps 0 to 7. Use access already configured on the agent instance |
| 4 | WordPress REST API with an existing application password | Same read only constraint |
| 5 | Unauthenticated HTTP observation | Headers, TTFB, status codes, certificates, endpoint reachability |
| 6 | Ask the user | For anything only they can see, such as the promotion plan or an admin only screen |
| 7 | UNKNOWN | Record the capability, the methods tried and the error |

Never ask the user to paste an SSH key, a password, an API token or a database credential into
chat. If a method needs a credential the agent does not already hold, that method is unavailable.
Say so and move down the ladder.

## Capability coverage

Primary below means the hosting platform MCP or the WordPress MCP as noted. On Cloudways
hosted sites the platform rows are served by the Cloudways MCP.

| Capability | Primary | Fallback | Fidelity lost |
| --- | --- | --- | --- |
| Server tier and specification | Platform MCP | Ask the user, or read from the platform UI with the user driving | None if answered |
| Current resource use | Platform MCP | Shell reads over SSH for load, memory, disk, inodes | Point in time only, no series |
| 90 day trends | Platform MCP | Any connected monitoring server, else the user's own record of last year | Projection becomes an assumption, label it |
| PHP workers | Platform MCP | Read the pool config over SSH, or infer from the tier and say it was inferred | Peak use unavailable, only the configured ceiling |
| Database metrics | Platform MCP | `wp db size`, status queries over SSH | Connection peak unavailable |
| Object cache state | Platform MCP | `wp cache type`, Redis info over SSH, or the object cache drop in | Hit rate may be unavailable |
| CDN and WAF | Platform MCP | Response headers reveal the edge and often the cache status | Configuration detail unavailable |
| Staging presence | Platform MCP | Ask the user | None if answered |
| Backups | Platform MCP | Ask the user, and require a timestamp not a schedule | Step 8 Class B and C stay blocked without a confirmed timestamp |
| Certificates | Platform MCP | Direct certificate inspection over HTTPS | None, HTTP observation is authoritative here |
| Core, plugin, theme inventory | WordPress MCP | `wp plugin list`, `wp theme list`, `wp core version` | None |
| Update status | WordPress MCP | `wp plugin list --update=available` | None |
| WooCommerce system status | WordPress MCP | `wp wc tool run`, or the report page read by the user | Slower, more gaps |
| Gateway configuration | WordPress MCP | `wp option get` on the gateway settings, presence and mode only | None, still never read secrets |
| Coupons | WordPress MCP | `wp wc shop_coupon list`, or ask the user to describe each | Configuration review becomes a conversation, sandbox tests still run |
| Order counts and ages | WordPress MCP | `wp wc shop_order list` with status and date filters, counted not listed | None, keep it aggregate |
| Action scheduler | WordPress MCP | `wp action-scheduler status` | None |
| Stock on promotion products | WordPress MCP | `wp wc product list` filtered to the named products | None |
| Cache exclusions | WordPress MCP | Observed headers across 5 requests per path | Configuration intent unavailable, observed behaviour is the stronger signal anyway |
| TTFB, LCP, third party weight | HTTP observation | None needed | None |
| Vulnerability data | A connected vulnerability source | None | Step 7 vulnerability check is UNKNOWN, never clean |

## When to actually stop

Stop and report BLOCKED only when no method on the ladder reaches a whole capability class, not
when the preferred one fails.

| Condition | Action |
| --- | --- |
| No platform access by any method | Step 2 and the tier recommendation are UNKNOWN. Continue with the rest |
| No site access by any method | That site is BLOCKED. Continue with the other sites |
| No access to any site by any method | Stop. Report BLOCKED for the whole run |
| Some capabilities missing | Continue. Record every UNKNOWN and say which conclusion is weakened |

A degraded audit that names its gaps is useful. A stopped audit is not. What is never acceptable is a
clean verdict resting on a check that never ran.

## Recording the method

Every finding already carries evidence and source. Where the source was anything other than rank 1,
name the method in the evidence field, for example `wp plugin list over SSH, 2026-11-05 14:22 UTC`.
Section 5 of the report lists every capability that fell back, with the rank used and what precision was
lost.

## Cost control

Pull the WooCommerce system status report first per site, by whichever method is available. It
answers a large share of Steps 1, 2, 4 and 7 in one call. Cache within a run, never read the same
value twice. Use aggregate order queries, never paginate order records.
