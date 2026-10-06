# Report template

No dashes, no emojis. Tables over prose. Lead with the verdict so a reader who stops after one
screen still knows whether their store is ready.

## Header

```
Run [timestamp and timezone]
Mode [manual or automatic]
Scope [n] sites, [account]
Black Friday [date]  Cyber Monday [date]
Freeze [start] through [end] inclusive
Days to freeze [n]
Previous run [date and link, or none]
```

If the window is open, replace the days line with a bold statement that routine change is suspended
and every remaining item is a risk decision.

## 1. Verdict

| Site | Verdict | P0 | P1 | P2 | P3 | Unknown |
| --- | --- | --- | --- | --- | --- | --- |

Fleet verdict [worst site verdict]

One paragraph. Actual state, largest single risk, what happens first. No padding.

Changes since last run [omit on a first run]

| Closed | New | Unchanged |
| --- | --- | --- |

## 2. P0 blockers

Nothing else matters until these clear. Say so in one line if empty.

| ID | Site | Finding | Evidence | Impact | Action | Owner | Fix by |
| --- | --- | --- | --- | --- | --- | --- | --- |

## 3. Findings by step

One subsection per step that ran, including clean ones, since a missing step reads as a failed step.

Step [n]. [Name]  Status [PASS, WARN, FAIL, UNKNOWN, NOT TESTABLE]

| ID | Severity | Finding | Evidence | Expected | Action | Fix by |
| --- | --- | --- | --- | --- | --- | --- |

## 4. Capacity and tier recommendation

Recommendation only, nothing has been changed.

| Resource | Current peak | Limit | Headroom multiple |
| --- | --- | --- | --- |

First to saturate [resource] at approximately [n]x
Projected peak [n]x, [measured from last year, or assumed, say which]
Assumptions [list, including what the audit cannot see]

| Option | Effect | Cost | Risk | Reversible |
| --- | --- | --- | --- | --- |

Recommended [option]  Apply by [date]  Reverse on [date]  Monthly delta [amount]  Peak period cost
[amount]

## 5. What was not checked

Not an appendix. A reader deciding whether to trust the verdict needs this.

| Check | Status | Reason | To close the gap |
| --- | --- | --- | --- |

Fallback sources used

| Capability | Method rank used | Precision lost |
| --- | --- | --- |

## 6. Fleet rollup

Only when more than one site is in scope.

| Finding | Sites affected | Severity | Single action that fixes all |
| --- | --- | --- | --- |

Fixing one root cause across eight sites is different work from eight unrelated problems. Say which
this is. Then list sites needing individual attention, and the suggested order of work ranked by
revenue at risk then effort, noting what can be batched.

## 7. Action plan

| Priority | Action | Site | Owner | Fix by | Depends on | Change class |
| --- | --- | --- | --- | --- | --- | --- |

Group by owner so each person sees their own list. Class comes from `references/remediation.md`
and tells the reader what could be executed under approval against what must be done by hand.

Pre freeze checklist. Ordered, each with its verification step so work is confirmed not assumed.

During the window. What to monitor, how often, and the threshold at which to act. Name the specific
Step 2 and Step 3 metrics.

After freeze end. The reversal register.

## 8. Change log

Only when Step 8 ran. Include it even when nothing was changed.

| Change ID | Finding | Site | Class | Approved by | Before | After | Verified | Outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

Reversal register

| Item | Applied | Reverse on | Reversal step |
| --- | --- | --- | --- |
