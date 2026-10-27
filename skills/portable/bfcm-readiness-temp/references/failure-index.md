# Failure index

Two uses. A check that the audit covered what actually breaks, and a symptom to cause index during
the sale.

## Symptom to cause, during the sale

| Symptom | Look at first |
| --- | --- |
| Traffic normal, orders near zero | Gateway mode, checkout cached, session stripped at the edge |
| Orders pending, gateway shows charges | Webhook blocked, rate limit tripping under load |
| Site fast, checkout times out | PHP workers exhausted, DB connections exhausted |
| Site slow everywhere | Cache hit rate, then CPU and memory |
| Totals wrong on some orders | Coupon stacking, tax on discounted total |
| Sale price not showing | Cron activation, then stale cache |
| Orders placed, nothing shipping | Action scheduler stalled, fulfilment webhook failing |
| Stock going negative | Oversell under concurrent checkout |
| Site down hard | Disk full, memory, DB connections |
| Payment taken, no order created | SameSite=Strict on the session cookie |

## Why these are missed

The dangerous class is silent. The site is up, monitoring is green, nobody is buying.

- Uptime monitoring hits cached pages. Cached pages cost no PHP workers. Checkout does. A site
  can pass every external check while every conversion fails
- Cache exclusions look right in the plugin while a CDN rule or a translated slug caches the path
  anyway. Configuration and observed headers disagree often enough that one check is not enough
- Concurrency defects cannot reproduce at normal traffic. Oversell and fragment saturation only
  appear when load arrives
- Asynchronous failures surface late. A failing fulfilment webhook becomes a support wave three
  days later, after the cause has scrolled out of the logs
- Cron behaves differently on staging. Low logged out traffic at the activation hour on a cached
  production site delays a midnight sale by hours
- Test mode follows a legitimate test nobody reverted, and the storefront gives no signal
- Auto update during the sale is the only failure here the store causes by doing nothing

## No rollback path

No recent backup, no staging, no way back. It turns every other item on this list from a problem into a
crisis, and it is why Step 1 caps the verdict when staging is absent and why Step 8 will not execute a
Class B or C change without a confirmed backup.
