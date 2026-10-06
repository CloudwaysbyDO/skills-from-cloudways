# Thresholds

Planning defaults for a typical WooCommerce store on managed hosting. Where the store's own 30
day baseline exists, the baseline wins and these become a sanity check. Say which was used. Never
present a default as a measurement of this store.

## Server, Step 2

| Metric | Pass | Warn | Fail |
| --- | --- | --- | --- |
| CPU, 7 day peak | Under 50% | 50 to 75% | Over 75% |
| Load average per core | Under 0.7 | 0.7 to 1.0 | Over 1.0 |
| Memory peak | Under 70% | 70 to 85% | Over 85% |
| Swap in and out | Near zero | Occasional | Continuous |
| Disk used | Under 70% | 70 to 85% | Over 85% |
| Inodes used | Under 70% | 70 to 85% | Over 85% |
| Days until disk full | Over 90 | 30 to 90 | Under 30, or inside freeze, P0 |
| PHP workers peak against configured | Under 50% | 50 to 70% | Over 70% |
| Max children reached, 30 days | 0 | 1 to 5 | Over 5 |
| DB connections peak against limit | Under 50% | 50 to 70% | Over 70% |
| Object cache hit rate | Over 90% | 75 to 90% | Under 75% |
| Object cache evictions | Near zero | Low, steady | Rising |
| Autoloaded options | Under 500 KB | 500 KB to 1 MB | Over 1 MB |
| Headroom multiple, first saturating resource | Over 5x | 3x to 5x | Under 3x |

## Performance, Step 3

| Metric | Pass | Warn | Fail |
| --- | --- | --- | --- |
| TTFB cached product page | Under 200 ms | 200 to 600 ms | Over 600 ms |
| TTFB uncached product page | Under 800 ms | 800 ms to 2 s | Over 2 s |
| TTFB cart page | Under 1 s | 1 to 2.5 s | Over 2.5 s |
| Uncached to cached ratio | Under 5x | 5x to 10x | Over 10x |
| LCP mobile, lab | Under 2.5 s | 2.5 to 4 s | Over 4 s |
| CLS | Under 0.1 | 0.1 to 0.25 | Over 0.25 |
| Full page cache hit rate | Over 85% | 60 to 85% | Under 60% |
| Third party scripts on critical path | 3 or fewer | 4 to 7 | Over 7 |
| Third party main thread time | Under 500 ms | 500 ms to 1.5 s | Over 1.5 s |
| Admin median response | Under 1 s | 1 to 3 s | Over 3 s |
| Render blocking third party | None on landing | Any on landing, P1 | Any on checkout, P1 |

## Checkout, Step 4, mostly binary

| Check | Fail condition |
| --- | --- |
| Cart, checkout, account cached | Any hit across 5 requests, P0 |
| Gateway mode on production | Test or sandbox, P0 |
| Gateway connectivity | Unconfirmed or failing, P0 |
| Webhook reachable and uncached | No, P0 |
| Session survives the CDN | No, P0 |
| SameSite on session cookie | Strict where an offsite redirect is used, P0 |
| Certificate expiry | Inside the window or within 14 days of it, P0 |
| Certificate chain | Missing intermediate, P1 |
| Fallback gateway | None, advisory |
| Cart fragments at projected peak | Over 30% of worker pool, P1. Pass under 15% |

## Orders, Step 5, all against the store's own 30 day baseline

| Metric | Pass | Warn | Fail |
| --- | --- | --- | --- |
| Pending payment, 1 to 7 days old | Under 1x normal | 1x to 3x | Over 3x |
| Pending payment, over 7 days | Under 1x | 1x to 2x | Over 2x |
| Failed order rate | At or below normal | Up to 1.5x | Over 1.5x |
| On hold, offline methods excluded | Under 1x | 1x to 2x | Over 2x |
| Paid but not progressed | 0 | Any, escalate | Any, escalate |
| Abandonment rate | At or below normal | Up to 1.3x | Over 1.3x |
| Oldest pending action past due | Under 5 min | 5 to 30 min | Over 30 min |
| Failed actions, 7 days | Under 0.1% | 0.1 to 1% | Over 1% |
| In progress action age | Under 5 min | 5 to 15 min | Over 15 min, orphaned |
| Queue arrival against drain | Drain wins | Roughly equal | Arrival wins |
| Zero totals, not legitimately free | 0 | 1 to 5 | Over 5 |
| Promotion stock against projected concurrent checkouts | Over 3x | 1x to 3x | Under 1x |

## Promotions, Step 6

| Check | Fail condition |
| --- | --- |
| Tested total against intended | Any difference |
| Effective discount against intent | Over 10 points above, P0. Pass within 2 points |
| Total against cost of goods | Below cost, P0 |
| Usage limit on a public code | Unlimited, P1 |
| Sale item exclusion | Not set where intended |
| Effective window in store time | Any mismatch with the campaign |
| Sale price activation path | WP Cron dependent, P1 |
| Tax on discounted total | Any mismatch |
| Shipping zones for campaign countries | Any gap, P0 |

## Currency, Step 7

| Metric | Pass | Warn | Fail |
| --- | --- | --- | --- |
| Core gap | Current | 1 minor | 2 or more minor, or any major |
| WooCommerce gap | Current | 1 minor | Any major |
| WooCommerce DB update pending | No | | Yes, P1 |
| Plugin last release age | Under 6 months | 6 to 12 months | Over 12 months |
| Actively exploited vulnerability | None | | Any, P0 |
| Critical or high unauthenticated | None | | Any, P0 |
| Removed from the directory | None | | Any, P0 |
| Auto updates during freeze | Off, except core security | Any non critical on | Any on a checkout path plugin |
| Worst case added checkout time | Under 2 s | 2 to 10 s | Over 10 s |
| PHP support status | Active | Security only | End of life |

## Applying

- Fail against a default with no baseline available is at most P1 unless the step names it P0
- Warn bands are findings, not noise. Report them, rank below fails
- Two warns in one causal chain, for example low hit rate plus high uncached TTFB, merge into one
  P1 with a single root cause rather than two separate warns
