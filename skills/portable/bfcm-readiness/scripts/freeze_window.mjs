#!/usr/bin/env node
/*
 * BFCM dates and change freeze window. Same rules and output as freeze_window.py, for runtimes
 * that have Node but no Python.
 *
 *   Thanksgiving   fourth Thursday of November
 *   Black Friday   day after Thanksgiving
 *   Cyber Monday   Monday after Black Friday
 *   Freeze start   Friday one week before Black Friday
 *   Freeze end     Wednesday after Cyber Monday, inclusive
 *   Prep window    8 weeks before Black Friday
 *
 * Fix by dates are business days before freeze start, weekends skipped. Public holidays
 * are not modelled, so pull a date earlier by hand if it lands on one.
 *
 *   node freeze_window.mjs
 *   node freeze_window.mjs --year 2026 --json
 *   node freeze_window.mjs --today 2026-11-24
 *
 * No dependencies. Dates are handled in UTC so the machine timezone never shifts a day.
 */

const DAY_MS = 86400000;
const THURSDAY = 3, FRIDAY = 4, WEDNESDAY = 2, MONDAY = 0;

const utc = (y, m, d) => new Date(Date.UTC(y, m - 1, d));
const addDays = (d, n) => new Date(d.getTime() + n * DAY_MS);
const iso = (d) => d.toISOString().slice(0, 10);
const diffDays = (a, b) => Math.round((a.getTime() - b.getTime()) / DAY_MS);
// Monday is 0, matching the Python version.
const weekday = (d) => (d.getUTCDay() + 6) % 7;

function thanksgiving(year) {
  const first = utc(year, 11, 1);
  const offset = (((THURSDAY - weekday(first)) % 7) + 7) % 7;
  return addDays(first, offset + 21);
}

function businessDaysBefore(d, n) {
  let moved = 0;
  while (moved < n) {
    d = addDays(d, -1);
    if (weekday(d) < 5) moved += 1;
  }
  return d;
}

function nextBusinessDay(d) {
  d = addDays(d, 1);
  while (weekday(d) >= 5) d = addDays(d, 1);
  return d;
}

function check(condition, message) {
  if (!condition) throw new Error("assertion failed: " + message);
}

function compute(year, today) {
  const blackFriday = addDays(thanksgiving(year), 1);
  const cyberMonday = addDays(blackFriday, 3);
  const freezeStart = addDays(blackFriday, -7);
  const freezeEnd = addDays(cyberMonday, 2);
  const prepStart = addDays(blackFriday, -56);

  check(weekday(blackFriday) === FRIDAY, "black friday is a friday");
  check(weekday(cyberMonday) === MONDAY, "cyber monday is a monday");
  check(weekday(freezeStart) === FRIDAY, "freeze start is a friday");
  check(weekday(freezeEnd) === WEDNESDAY, "freeze end is a wednesday");

  const reversal = nextBusinessDay(freezeEnd);
  return {
    year: year,
    today: iso(today),
    black_friday: iso(blackFriday),
    cyber_monday: iso(cyberMonday),
    prep_window_start: iso(prepStart),
    freeze_start: iso(freezeStart),
    freeze_end: iso(freezeEnd),
    days_until_freeze_start: diffDays(freezeStart, today),
    days_until_black_friday: diffDays(blackFriday, today),
    inside_freeze_window: freezeStart <= today && today <= freezeEnd,
    inside_prep_window: prepStart <= today && today <= freezeEnd,
    fix_by: {
      P0: iso(businessDaysBefore(freezeStart, 5)),
      P1: iso(businessDaysBefore(freezeStart, 2)),
      P2: iso(freezeStart),
      P3: iso(reversal),
    },
    reversal_date: iso(reversal),
  };
}

function render(r) {
  const out = [
    "BFCM " + r.year,
    "",
    "  Black Friday       " + r.black_friday,
    "  Cyber Monday       " + r.cyber_monday,
    "  Prep window opens  " + r.prep_window_start,
    "  Freeze start       " + r.freeze_start,
    "  Freeze end         " + r.freeze_end + " inclusive",
    "",
    "  Today              " + r.today,
    "  Days to freeze     " + r.days_until_freeze_start,
    "  Inside freeze      " + (r.inside_freeze_window ? "YES" : "no"),
    "  Inside prep window " + (r.inside_prep_window ? "YES" : "no"),
    "",
    "  Fix by",
    "    P0               " + r.fix_by.P0,
    "    P1               " + r.fix_by.P1,
    "    P2               " + r.fix_by.P2,
    "    P3               " + r.fix_by.P3,
    "",
    "  Reversal date      " + r.reversal_date,
  ];
  if (r.inside_freeze_window) {
    out.push(
      "",
      "  FREEZE WINDOW OPEN. Routine change suspended. Each remaining item",
      "  is a risk decision, not a scheduled fix."
    );
  }
  return out.join("\n");
}

function fail(message) {
  process.stderr.write("freeze_window.mjs: " + message + "\n");
  process.exit(2);
}

function parseArgs(argv) {
  const args = { year: null, today: null, json: false };
  for (let i = 0; i < argv.length; i++) {
    const [flag, inline] = argv[i].split(/=(.*)/s);
    if (flag === "--json") {
      args.json = true;
    } else if (flag === "--year" || flag === "--today") {
      const value = inline !== undefined ? inline : argv[++i];
      if (value === undefined) fail(flag + " needs a value");
      args[flag.slice(2)] = value;
    } else {
      fail("unknown argument " + argv[i]);
    }
  }
  return args;
}

function parseDate(text) {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(text);
  const d = m && utc(Number(m[1]), Number(m[2]), Number(m[3]));
  if (!d || iso(d) !== text) fail("invalid date '" + text + "', expected YYYY-MM-DD");
  return d;
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  let today;
  if (args.today) {
    today = parseDate(args.today);
  } else {
    const now = new Date();
    today = utc(now.getFullYear(), now.getMonth() + 1, now.getDate());
  }

  let year;
  if (args.year !== null) {
    if (!/^\d{4}$/.test(args.year)) fail("invalid year '" + args.year + "'");
    year = Number(args.year);
  } else {
    year = today.getUTCFullYear();
    if (today > parseDate(compute(year, today).freeze_end)) year += 1;
  }

  const result = compute(year, today);
  process.stdout.write((args.json ? JSON.stringify(result, null, 2) : render(result)) + "\n");
}

main();
