# Audit steps 0 to 7

Read only. Score every measurement against `references/thresholds.md`. Source data per
`references/data-sources.md`, which is the hosting platform MCP and WordPress MCP by default
with a fallback ladder under each capability.

## Step 0. Prerequisites and freeze window

- Platform MCP responds, and metrics return real series not empty ones. Metrics missing means
  Step 2 trends are UNKNOWN, not PASS
- WordPress MCP responds for every site, not a sample. Record WordPress version, WooCommerce
  present, credential expiry if readable
- For anything that does not respond, work down the ladder in `references/data-sources.md` and
  record which rank answered
- Get today's date from the runtime, then read the year's row in `references/freeze-window.md` for
  the dates, the fix by dates, and whether the window is already open
- Record audit timestamp, store timezone per site, account identity, scope, mode, and the access
  method used per capability

Do not stop because an MCP is missing. Stop only when no method reaches a capability class at all.

| Condition | Action |
| --- | --- |
| No platform access by any method | Step 2 and the tier recommendation are UNKNOWN, continue |
| No access to one site by any method | That site is BLOCKED, continue with the others |
| No access to any site by any method | Stop, report BLOCKED for the run |

When stopping, state what failed, the error, what cannot be assessed, and the one action to
unblock. Partial fleet access is never a full stop. Audit what is reachable and keep the unreachable
sites visible in the rollup.

## Step 1. Inventory

Enumerate applications, present the list, confirm scope in one question. Do not proceed on silence.
Echo back and continue if the user already named sites.

Capture per site.

- Tier, cores, RAM, disk, region. PHP version and support status. Core, WooCommerce and
  database versions
- Active and inactive plugins with versions. Theme and parent. Must use plugins and drop ins, a
  frequent blind spot
- Full page cache, object cache, OPcache, CDN scope, WAF or bot management
- Staging present and its freshness, deployment path, backup schedule and last successful backup

No staging caps the verdict at READY WITH RISK and makes Step 6 NOT TESTABLE. Nothing found
can be safely fixed on that site. Staging older than 30 days or drifted from production makes Step 6
results indicative only.

Flags to raise here. PHP end of life P1. Core two or more minors behind P2. WooCommerce a major
behind P1. No staging P1. No object cache P1. No full page cache P1. No backup in 24 hours P0.
Inactive plugins P2, they still carry vulnerability exposure on disk.

## Step 2. Server health, performance and trends

Capture current, 7 day average and 7 day peak.

- CPU and load average per core. Memory used, free, cached, plus swap in and out rate. Swap
  activity matters more than swap allocated
- Disk percentage and absolute free, every mount. Inodes, a full inode table fails writes while disk
  still shows free
- PHP workers configured, peak use, max children reached events, request duration held
- DB connection limit and peak, slow query count, table sizes with attention to `wp_options` and the
  action scheduler tables, autoloaded options size, InnoDB buffer pool against database size
- Object cache hit rate, evictions, memory allocated against used, drop in present and matching.
  Low hit rate with high evictions means too small, not useless

90 day trends. Report baseline as the 30 day median excluding spike days, direction and rate, and
any step change with its start date. For disk report days until full. If that date lands inside the
freeze window it is P0 regardless of current percentage.

Projection. Last year peak against last year baseline gives a multiplier. Apply to this year's
baseline. If last year's data is missing, use a 3x to 5x planning range and label it an assumption,
never as this account's own history.

Saturation. For each resource compute `limit / current_peak`. Rank lowest first. The lowest is the
saturation point, state it plainly. Note the non linearity, uncached request volume drives worker and
database pressure, not total traffic, so a higher converting campaign costs more than a bigger one.

Tier recommendation, recommendation only. Current tier and cost, recommended tier sized for 1.5x
margin over projected peak, cost delta, upgrade date at least 5 business days before freeze start,
reversal date the first business day after freeze end, and whether downgrade is supported.

List non upgrade options first where they clear the bottleneck, since they cost nothing and reverse
instantly. Raising workers within the tier, raising the DB connection limit, increasing object cache
memory, reducing autoloaded options, repairing full page caching.

## Step 3. Performance baseline

Method. Three runs, report the median. Record cache status header and client location. Never warm
then measure. Never load test production.

- TTFB on cached product page, uncached product page, cart page. Report the uncached to cached
  ratio, that ratio is the penalty per cache miss
- LCP on the intended BFCM landing page, mobile and desktop, plus the LCP element and whether
  the image is preloaded and sized. Ask which page, do not assume the homepage. Also CLS, since
  injected banners and countdown timers shift layout
- Full page cache hit rate from the cache layer, not a plugin dashboard. Which URL patterns miss.
  Whether a site wide cookie disables caching for everyone, which is P0 and usually comes from
  analytics, currency, geolocation or a consent banner
- Third party scripts, origin, size, execution time, render blocking or not, and whether they load on
  checkout. Render blocking on the landing page is P1. Non essential on checkout is P1
- Admin response on orders list, products list, dashboard. Slow admin consumes the same worker
  pool as checkout

Record the baseline with timestamps. It is the comparison point for Step 8 verification and for
judging whether the site is slow or merely busy during the sale.

## Step 4. Checkout and payment path

Cache exclusions, checked twice. Configuration across server cache, caching plugin, CDN rules and
any page caching object cache. Then observed headers, 5 requests per path, with and without a
session cookie. A hit on any request is conclusive and is P0. Cover `/cart`, `/checkout`,
`/my-account`, `/wc-api/*`, `?wc-ajax=*`, `/wp-json/wc/`, order received, and every translated or
custom slug. The multilingual case is the most common real miss.

Cart fragments. Enabled, scope, cost per request, requests per page view, projected load at peak.
Fragments fire on cached pages too, so the cache gives no protection. Over 30 percent of the worker
pool at projected peak is P1. Name the trade off, disabling them makes the mini cart count stale.

Sessions through cache and CDN. Session cookie attributes, CDN forwards and does not strip cart
and session cookies, Vary not collapsed, session backend and whether it survives an object cache
flush, garbage collection running. `SameSite=Strict` breaks return from an offsite gateway redirect,
which presents as payment taken and no order, P0.

Gateways. Enabled, mode live or test, connectivity, credential expiry, methods enabled against what
the campaign advertises, plugin version, gateway API version deprecation, currency match, country
and amount restrictions a promotion could trip. Test mode on production is P0 and usually follows a
legitimate test nobody reverted. Also record whether a fallback gateway exists and is enabled, since
one gateway is a single point of failure on the highest revenue day.

Webhooks and callbacks. Endpoint responds with an expected status not a redirect or challenge,
uncached, not blocked by firewall, rate limiting, security plugin or maintenance mode, reachable on
the protocols the gateway uses, gateway delivery log shows successes. Check WooCommerce
webhooks and any fulfilment, ERP or accounting hook too. Confirm gateway sources are allow listed
rather than merely under the current rate limit, since callback volume scales with orders.

Certificates. Expiry for every domain in the checkout path including the CDN edge, auto renewal
working, full chain served. Expiry inside the freeze window is P0. A missing intermediate works in
desktop browsers and fails on mobile and server to server, which makes it look intermittent.

Stop and escalate if money cannot move. Gateway in test mode, gateway not connecting, checkout
path cached, callback blocked or cached, certificate expired or expiring in the window, session
broken through the CDN. State the finding, evidence, exact remediation, and that the store currently
cannot reliably take payment. Do not soften it and do not continue to Step 5 first.

## Step 5. Cart and order health

Counts and ages only. If a tool returns full records, take status, timestamp and total and discard the
rest without writing it anywhere.

Baseline first. Orders per day median over 30 days excluding promotions, status distribution,
abandonment rate, median pending to processing and processing to completed. Report every count
as an absolute and as a multiple of normal. Forty pending orders means nothing without knowing
whether the store does 20 or 2000 a day.

- Open carts, abandoned volume against normal, abandoned cart table size. A rise above normal is a
  checkout defect signal, not a marketing signal, cross reference Step 4
- Pending payment bucketed by age, under 1 hour, 1 to 24 hours, 1 to 7 days, over 7 days. Exclude
  offline methods and say which. Accumulation in the 1 to 7 day bucket while the gateway shows
  charges is the classic blocked webhook signature
- On hold and failed with age distribution, failed rate against normal, and whether failures cluster
  on one gateway, method, currency or country. A cluster names the cause
- Paid but never progressed. Transaction identifier present or paid date set while status stays
  pending or failed. Record presence only, never the value. Any non zero count escalates. If
  webhooks test clean but paid orders strand, the block is intermittent, usually rate limiting under
  load
- Action scheduler, pending count and oldest past due, failed by hook over 7 days, in progress older
  than 15 minutes meaning orphaned, table row count, and whether it runs on WP Cron or real cron.
  Report drain rate against arrival rate, not just depth. WP Cron fires on page requests, so on a
  cached site it fires rarely and competes with checkout for workers
- Zero or missing totals not legitimately free. Cause is usually a coupon over discounting, a tax or
  currency failure, or an interrupted checkout. Report the count and cause class, do not open the
  orders
- Stock on promotion products. Ask which products are in the promotion, do not guess from what is
  currently on sale. Capture stock management level, quantity, backorder setting, low stock
  threshold, parent against variation level. Stock reduces at order placement, not at cart entry, so
  concurrent checkouts can pass the same check. Rank by stock depth against projected concurrent
  checkouts, state exposure in units, and let the store choose between backorders, more stock, or
  accepting the risk. Any promotion product out of stock, hidden, in draft or missing a sale price
  is P0

Escalate on any paid but not progressed, failed rate above normal, pending above 3x normal, a
backlog growing across two observations, or an unpurchasable promotion product.

## Step 6. Promotions and pricing

Staging only, sandbox gateway. Confirm staging by two independent signals, not by the word staging
in a name. No staging means the whole step is NOT TESTABLE and the Step 1 no staging finding
rises to P0 for the promotion period. Never report an untested coupon as passing.

Get the plan first. Code, intended discount, scope, audience, start and end, intended stacking. No
written plan is itself the finding.

Configuration review per coupon. Discount type, fixed cart and fixed product get confused
constantly. Amount. Usage limit, unlimited on a public code is P1 once it reaches a deal aggregator.
Per user limit, which does nothing on a guest checkout store. Product and category rules. Sale item
exclusion, the most common margin leak. Minimum and maximum spend. Individual use only.
Allowed emails. Free shipping flag.

Expiry and timezone. Store timezone, server timezone, and each coupon's exact effective moment in
store time. WooCommerce expiry applies at the end of the expiry date in store time, so a coupon set
to expire the day before the sale ends is dead for the final day. State the effective window and ask
the user to confirm it matches the campaign. Date only expiry cannot express an hour, flag any
promotion that needs one.

Sandbox checkout per coupon. Record subtotal, discount, tax, shipping, total, expected total,
difference. A coupon that applies is not a coupon that is correct, the check is cent exact. Test a
qualifying cart, just below and just above minimum spend, an excluded product, a sale item, a
second redemption by the same user, and guest checkout.

Stacking. Test everything not explicitly blocked, including combinations nobody planned, because
customers find them. Coupon with sale price, coupon with coupon, coupon with an automatic cart
discount, with free shipping, with store credit or points, with a subscription or bundle discount.
Compute `(list_total - final_total) / list_total` and compare to intent. More than 10 points above
intent is P0. Below cost of goods is P0. Ask for cost of goods, and without it say margin cannot be
computed rather than guessing.

Sale price activation. Scheduled prices run through the action scheduler, often on WP Cron. On a
cached site with low logged out traffic at the activation hour, a midnight sale can activate at 07:00.
Recommend real cron, manual verification at start time, and a cache purge step since cached pages
serve stale prices after activation. Test activation on staging.

Tax on discounted totals. Inclusive or exclusive pricing, discount before or after tax, tax on each
tested discounted total, rounding per line or per cart and drift across many lines, tax exempt
customer with a coupon, at least one domestic and one cross border case. State the per order error
and multiply by projected volume.

Free shipping thresholds. Whether the threshold evaluates before or after the discount, a cart that
qualifies before and falls below after, a free shipping coupon case, and whether the storefront
amount remaining prompt uses the same calculation as the shipping method. Both behaviours are
defensible, the storefront promising and the checkout charging is not. Confirm shipping zones cover
every country the campaign targets, a gap is P0.

## Step 7. Plugin, theme and core currency

Updating is a risk and not updating is a risk. Name both sides. A blanket update everything
recommendation three days before a sale is bad advice.

- Per plugin and theme, installed version, latest, gap in major, minor and patch, installed version
  age, whether the update is a security release or carries a breaking change. Sort by risk, not
  alphabetically. Report total out of date and separately the count more than one major behind,
  which predicts how painful the eventual update will be
- Core and WooCommerce versions and gaps, whether the installed core still receives security
  backports, whether the gateway plugins still support the installed WooCommerce, which is the
  dependency that actually bites, and whether a WooCommerce database update is pending, which is
  P1 on its own because it means new code against an old schema
- Vulnerability cross reference. Identifier, severity, whether actively exploited, fixed version, any
  mitigation short of updating. Actively exploited is P0 at any score and is the one case where
  updating inside the freeze window is correct. Critical or high unauthenticated is P0. Name the data
  source and its date. With no source available, mark this UNKNOWN, never clean. A clean result
  that was never checked is the most dangerous output this skill can produce
- Abandoned or removed, listed separately as a replacement decision. Removed from the directory,
  untested with the last 3 core releases, no release in 12 months, publicly discontinued, or no
  vendor response in 6 months. Report what it does, whether it is on the checkout path, replacement
  candidates, migration effort, and defer unless it carries an active vulnerability. Removed from the
  directory is P0 even with no published advisory
- No update in over a year, listed separately from abandoned, since stable is legitimate for a small
  focused plugin. Note current core testing and PHP 8 compatibility
- Auto updates. Per plugin and theme settings, core policy, any platform level updater, any plugin
  that forces its own updates, scheduled update jobs, and whether a core major is expected inside
  the window. Every enabled auto update is an unreviewed change that can land on Black Friday.
  Recommend disabling for the window with two carve outs, core security releases and anything
  actively exploited, and give the reversal date so they come back on rather than staying off forever
- Order completion hooks. Everything on `woocommerce_thankyou`, the status transition hooks,
  `woocommerce_payment_complete`, `woocommerce_new_order`,
  `woocommerce_checkout_order_processed`. Record hook, priority, synchronous or deferred,
  external HTTP call and to which service, timeout value, and failure behaviour. Sum the
  synchronous external timeouts to give worst case added checkout time. That number is usually far
  larger than anyone expects and is the strongest argument for moving the work to the queue.
  Where the plugin will not defer, a shortened timeout is the low risk fix
