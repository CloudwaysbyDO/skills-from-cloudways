# Freeze window

Use the table. No execution required. The script in `scripts/` is an optional accelerator for runtimes
that have a shell, not a dependency.

## Dates

All dates inclusive. Freeze end is the last day of the window.

| Year | Black Friday | Cyber Monday | Prep opens | Freeze start | Freeze end | P0 by | P1 by | P2 by | Reversal |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026 | 2026-11-27 | 2026-11-30 | 2026-10-02 | 2026-11-20 | 2026-12-02 | 2026-11-13 | 2026-11-18 | 2026-11-20 | 2026-12-03 |
| 2027 | 2027-11-26 | 2027-11-29 | 2027-10-01 | 2027-11-19 | 2027-12-01 | 2027-11-12 | 2027-11-17 | 2027-11-19 | 2027-12-02 |
| 2028 | 2028-11-24 | 2028-11-27 | 2028-09-29 | 2028-11-17 | 2028-11-29 | 2028-11-10 | 2028-11-15 | 2028-11-17 | 2028-11-30 |
| 2029 | 2029-11-23 | 2029-11-26 | 2029-09-28 | 2029-11-16 | 2029-11-28 | 2029-11-09 | 2029-11-14 | 2029-11-16 | 2029-11-29 |
| 2030 | 2030-11-29 | 2030-12-02 | 2030-10-04 | 2030-11-22 | 2030-12-04 | 2030-11-15 | 2030-11-20 | 2030-11-22 | 2030-12-05 |
| 2031 | 2031-11-28 | 2031-12-01 | 2031-10-03 | 2031-11-21 | 2031-12-03 | 2031-11-14 | 2031-11-19 | 2031-11-21 | 2031-12-04 |
| 2032 | 2032-11-26 | 2032-11-29 | 2032-10-01 | 2032-11-19 | 2032-12-01 | 2032-11-12 | 2032-11-17 | 2032-11-19 | 2032-12-02 |
| 2033 | 2033-11-25 | 2033-11-28 | 2033-09-30 | 2033-11-18 | 2033-11-30 | 2033-11-11 | 2033-11-16 | 2033-11-18 | 2033-12-01 |

Get today's date from the runtime, never from memory or from training data. Then read the row and
determine three things.

1. Days until freeze start
2. Whether today falls between freeze start and freeze end, which flips the skill to risk decision mode
3. Whether today falls between prep opens and freeze end, which is one condition for automatic
   triggering

If today is after freeze end, use next year's row.

## Rules the table implements

- Black Friday, the day after the fourth Thursday of November
- Cyber Monday, the following Monday
- Freeze start, the Friday one week before Black Friday
- Freeze end, the Wednesday after Cyber Monday
- Prep opens, 8 weeks before Black Friday
- P0 by, 5 business days before freeze start. P1 by, 2 business days before. P2 by, freeze start. P3
  and reversal, the first business day after freeze end

Public holidays are not modelled. A fix by date landing on a holiday moves earlier.

## Beyond 2033

Derive from the rules above, or run the script if the runtime has a shell. Sanity check the result.
Black Friday and freeze start must both be Fridays, Cyber Monday a Monday, freeze end a
Wednesday. If any of those fail, the arithmetic is wrong.

## Optional script

Build the command using the path form given in the resolving paths table in SKILL.md, then append
one of these argument sets.

```
--json
--year 2029
--today 2026-11-24
```

Hermes runs `freeze_window.py`, which needs Python 3.7 or later. OpenClaw runs `freeze_window.mjs`,
which needs Node and prints identical output. Both need a shell tool in the runtime. They assert the
weekday of every derived date and fail loudly rather than returning a wrong answer. If the runtime
has no shell, or neither Python nor Node is present, ignore them. The table above is the source of
truth and the table and both scripts come from the same rules.
