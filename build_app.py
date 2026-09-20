import json

import sys
from pathlib import Path

script_dir = Path(__file__).parent
with open(script_dir / 'classes_min.json') as f:
    data_json = f.read()

capacity_lookup_path = script_dir / 'capacity_lookup.json'
if capacity_lookup_path.exists():
    with open(capacity_lookup_path) as f:
        capacity_lookup_json = f.read()
else:
    capacity_lookup_json = '{}'
    print(f"WARNING: {capacity_lookup_path} not found; capacity badges will be empty.", file=sys.stderr)

html = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Class Finder">
<meta name="mobile-web-app-capable" content="yes">
<meta name="theme-color" content="#0f1115">
<title>Class Finder</title>
<style>
  :root {
    --bg: #0f1115;
    --card: #171a21;
    --card-border: #262a35;
    --accent: #6ee7b7;
    --accent2: #34d399;
    --text: #e6e8ec;
    --muted: #8a91a3;
    --chip-bg: #1f2430;
    --chip-active: #34d399;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    padding: 16px;
    padding-bottom: 60px;
  }
  h1 {
    font-size: 20px;
    margin: 0 0 4px 0;
    font-weight: 700;
  }
  .subtitle {
    color: var(--muted);
    font-size: 13px;
    margin-bottom: 18px;
  }
  .section {
    background: var(--card);
    border: 1px solid var(--card-border);
    border-radius: 14px;
    padding: 14px;
    margin-bottom: 12px;
  }
  .section-title {
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--muted);
    margin-bottom: 10px;
    font-weight: 600;
  }
  .day-row, .view-row {
    display: flex;
    gap: 6px;
    overflow-x: auto;
  }
  .chip {
    flex: 0 0 auto;
    padding: 8px 12px;
    border-radius: 10px;
    background: var(--chip-bg);
    color: var(--text);
    font-size: 13px;
    font-weight: 600;
    border: 1px solid transparent;
    cursor: pointer;
    user-select: none;
    white-space: nowrap;
  }
  .chip.active {
    background: var(--chip-active);
    color: #06231a;
    border-color: var(--chip-active);
  }
  .chip.small {
    font-size: 12px;
    padding: 7px 10px;
    font-weight: 500;
  }
  .chip.wide {
    flex: 1 1 0;
    text-align: center;
    padding: 8px 4px;
    font-size: 12px;
  }
  .chip-wrap {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }
  .timeofday-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 6px;
  }
  select, input[type=text] {
    width: 100%;
    padding: 10px 12px;
    border-radius: 10px;
    border: 1px solid var(--card-border);
    background: var(--chip-bg);
    color: var(--text);
    font-size: 14px;
  }
  input[type=number].ab-time {
    padding: 8px 6px;
    border-radius: 8px;
    border: 1px solid var(--card-border);
    background: var(--chip-bg);
    color: var(--text);
    font-size: 14px;
    text-align: center;
  }
  .ab-row {
    display: flex;
    gap: 4px;
    align-items: center;
    flex-wrap: wrap;
    margin-bottom: 10px;
  }
  .ab-sep {
    color: var(--muted);
    font-weight: 700;
  }
  .ab-result-row {
    display: flex;
    justify-content: space-between;
    gap: 8px;
    padding: 8px 10px;
    border-radius: 8px;
    background: var(--chip-bg);
    border: 1px solid var(--card-border);
    margin-bottom: 6px;
    font-size: 13px;
  }
  .ab-result-row.ok { border-color: var(--accent2); }
  .ab-result-row.fail { border-color: #f87171; }
  .ab-result-row.skip { opacity: 0.65; }
  .ab-status-tag {
    font-weight: 700;
    flex: 0 0 auto;
  }
  .filter-toggle {
    display: flex;
    justify-content: space-between;
    align-items: center;
    cursor: pointer;
  }
  .filter-toggle .arrow {
    color: var(--muted);
    font-size: 12px;
    transition: transform 0.2s;
  }
  .filter-toggle.open .arrow {
    transform: rotate(180deg);
  }
  .collapsible {
    display: none;
  }
  .collapsible.open {
    display: block;
    margin-top: 12px;
  }
  .ms-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }
  .ms-block {
    margin-bottom: 16px;
  }
  .ms-block:last-child {
    margin-bottom: 0;
  }
  input[type=text].ms-search {
    margin-bottom: 8px;
  }
  .scroll-box {
    max-height: 220px;
    overflow-y: auto;
    padding-right: 2px;
  }
  .active-filters {
    font-size: 12px;
    color: var(--accent);
    margin-top: 6px;
  }
  .clear-link {
    font-size: 12px;
    color: var(--muted);
    text-decoration: underline;
    cursor: pointer;
    margin-left: 8px;
  }
  .narrow-hint {
    font-size: 11.5px;
    color: var(--accent);
    margin: -2px 0 8px 0;
  }
  .results-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin: 18px 0 10px 0;
  }
  .results-count {
    font-size: 14px;
    font-weight: 600;
    color: var(--text);
  }
  .sort-select {
    font-size: 12px;
    padding: 6px 8px;
    width: auto;
  }
  .class-card {
    background: var(--card);
    border: 1px solid var(--card-border);
    border-left: 3px solid var(--accent2);
    border-radius: 12px;
    padding: 12px 14px;
    margin-bottom: 8px;
  }
  .day-group-header {
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--muted);
    margin: 16px 0 8px 0;
  }
  .day-group-header:first-child {
    margin-top: 0;
  }
  .class-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 8px;
  }
  .class-name {
    font-size: 15px;
    font-weight: 700;
    color: var(--text);
  }
  .class-time {
    font-size: 13px;
    font-weight: 700;
    color: var(--accent);
    white-space: nowrap;
  }
  .class-meta {
    font-size: 12.5px;
    color: var(--muted);
    margin-top: 4px;
  }
  .avail-badge {
    display: inline-block;
    font-size: 11px;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 999px;
    margin-left: 6px;
    white-space: nowrap;
  }
  .avail-ok {
    background: rgba(52, 211, 153, 0.15);
    color: var(--accent2);
  }
  .avail-low {
    background: rgba(251, 191, 36, 0.15);
    color: #fbbf24;
  }
  .avail-wait {
    background: rgba(248, 113, 113, 0.15);
    color: #f87171;
  }
  .avail-full {
    background: rgba(138, 145, 163, 0.15);
    color: var(--muted);
  }
  .avail-cap {
    background: rgba(138, 145, 163, 0.12);
    color: var(--muted);
    font-weight: 600;
  }

  /* Live availability login */
  .live-status-line {
    font-size: 12px;
    color: var(--muted);
    margin-bottom: 8px;
  }
  .live-error {
    font-size: 12px;
    color: #f87171;
    margin-bottom: 8px;
    display: none;
  }
  .live-disclaimer {
    font-size: 11.5px;
    color: var(--muted);
    background: rgba(251, 191, 36, 0.08);
    border: 1px solid rgba(251, 191, 36, 0.25);
    border-radius: 8px;
    padding: 8px 10px;
    margin-bottom: 10px;
    line-height: 1.4;
  }
  .live-field {
    margin-bottom: 8px;
  }
  .live-field label {
    display: block;
    font-size: 12px;
    color: var(--muted);
    margin-bottom: 4px;
  }
  .live-remember-row {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12.5px;
    color: var(--muted);
    margin-bottom: 10px;
  }
  .live-btn {
    padding: 9px 14px;
    border-radius: 10px;
    background: var(--chip-active);
    color: #06231a;
    font-size: 13px;
    font-weight: 700;
    border: none;
    cursor: pointer;
  }
  .live-btn:disabled {
    opacity: 0.6;
    cursor: default;
  }
  .live-secondary-btn {
    padding: 8px 12px;
    border-radius: 10px;
    background: var(--chip-bg);
    color: var(--text);
    font-size: 12.5px;
    font-weight: 600;
    border: 1px solid var(--card-border);
    cursor: pointer;
    margin-right: 8px;
  }
  .live-loggedin-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 8px;
  }
  .empty-state {
    text-align: center;
    color: var(--muted);
    padding: 40px 10px;
    font-size: 14px;
  }
  .empty-state .big {
    font-size: 28px;
    margin-bottom: 8px;
  }

  /* Weekly grid view */
  .week-scroll {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    border: 1px solid var(--card-border);
    border-radius: 12px;
  }
  table.week-grid {
    border-collapse: collapse;
    width: 100%;
    min-width: 900px;
  }
  table.week-grid th, table.week-grid td {
    border: 1px solid var(--card-border);
    vertical-align: top;
    padding: 6px;
  }
  table.week-grid th {
    background: #1b1f29;
    color: var(--muted);
    font-size: 11.5px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    position: sticky;
    top: 0;
    z-index: 2;
  }
  table.week-grid th.center-col, table.week-grid td.center-col {
    position: sticky;
    left: 0;
    background: #1b1f29;
    z-index: 3;
    min-width: 128px;
    max-width: 128px;
    font-size: 12px;
    font-weight: 700;
    color: var(--text);
    pointer-events: none;
  }
  table.week-grid td {
    min-width: 118px;
    max-width: 118px;
    background: var(--card);
  }
  .week-slot {
    background: var(--chip-bg);
    border-left: 2px solid var(--accent2);
    border-radius: 6px;
    padding: 4px 6px;
    margin-bottom: 4px;
    font-size: 11px;
    line-height: 1.35;
  }
  .week-slot:last-child { margin-bottom: 0; }
  .week-slot .t { font-weight: 700; color: var(--accent); display: block; }
  .week-slot .c { font-weight: 600; color: var(--text); display: block; }
  .week-slot .i { color: var(--muted); display: block; }
  .week-hint {
    font-size: 11.5px;
    color: var(--muted);
    margin-top: 8px;
    text-align: center;
  }

  /* Add-to-plan controls */
  .plan-btn {
    flex: 0 0 auto;
    padding: 6px 10px;
    border-radius: 8px;
    background: var(--chip-bg);
    color: var(--accent);
    font-size: 11.5px;
    font-weight: 700;
    border: 1px solid var(--card-border);
    cursor: pointer;
    user-select: none;
    white-space: nowrap;
  }
  .plan-btn.in-plan {
    background: var(--accent2);
    color: #06231a;
    border-color: var(--accent2);
  }
  .book-btn {
    flex: 0 0 auto;
    padding: 6px 10px;
    border-radius: 8px;
    background: #f87171;
    color: #2a0a0a;
    font-size: 11.5px;
    font-weight: 700;
    border: 1px solid #f87171;
    cursor: pointer;
    user-select: none;
    white-space: nowrap;
    margin-left: 6px;
  }
  .book-btn:disabled {
    opacity: 0.6;
    cursor: default;
  }
  .book-btn.booked {
    background: var(--accent2);
    color: #06231a;
    border-color: var(--accent2);
    opacity: 1;
  }
  .week-slot {
    position: relative;
  }
  .week-slot .plan-btn {
    margin-top: 4px;
    padding: 3px 6px;
    font-size: 10px;
  }
  .week-slot .book-btn {
    margin-top: 4px;
    margin-left: 4px;
    padding: 3px 6px;
    font-size: 10px;
  }

  /* My Plan view */
  .plan-day-header {
    font-size: 13px;
    font-weight: 800;
    color: var(--text);
    margin: 18px 0 8px 0;
    padding-bottom: 4px;
    border-bottom: 1px solid var(--card-border);
  }
  .plan-day-header:first-child { margin-top: 0; }
  .plan-center-header {
    font-size: 12px;
    font-weight: 700;
    color: #06231a;
    padding: 5px 10px;
    border-radius: 8px;
    margin: 10px 0 6px 0;
    display: inline-block;
  }
  .plan-session-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: var(--card);
    border: 1px solid var(--card-border);
    border-radius: 10px;
    padding: 9px 12px;
    margin-bottom: 6px;
  }
  .plan-session-info .t {
    font-size: 13px;
    font-weight: 700;
    color: var(--accent);
  }
  .plan-session-info .c {
    font-size: 13.5px;
    font-weight: 600;
    color: var(--text);
    margin-left: 6px;
  }
  .plan-session-info .i {
    font-size: 12px;
    color: var(--muted);
    display: block;
    margin-top: 2px;
  }
  .plan-remove {
    flex: 0 0 auto;
    color: var(--muted);
    font-size: 18px;
    padding: 0 4px;
    cursor: pointer;
  }

  .print-title {
    display: none;
  }

  @media print {
    body { background: #fff; color: #000; padding: 0; }
    .no-print { display: none !important; }
    .plan-remove { display: none !important; }
    .print-title {
      display: block;
      font-size: 18px;
      font-weight: 800;
      margin-bottom: 4px;
    }
    .print-subtitle {
      display: block;
      font-size: 12px;
      color: #555;
      margin-bottom: 16px;
    }
    .plan-day-header { color: #000; border-bottom-color: #999; }
    .plan-center-header { color: #000; }
    .plan-session-row {
      background: #fff;
      border-color: #ccc;
      break-inside: avoid;
    }
    .plan-session-info .t { color: #000; }
    .plan-session-info .c { color: #000; }
    .plan-session-info .i { color: #444; }
    .results-count { color: #000; }
  }
</style>
</head>
<body>

<h1 class="no-print">Class Finder</h1>
<div class="subtitle no-print">Find classes, or build a weekly schedule &middot; data as of __BUILD_DATE__ &middot; <a href="membership.html" style="color:var(--accent);">Membership Calculator &rarr;</a></div>

<div class="section no-print">
  <div class="section-title">View</div>
  <div class="view-row">
    <div class="chip wide active" id="viewListBtn">List by day</div>
    <div class="chip wide" id="viewWeekBtn">Weekly schedule</div>
    <div class="chip wide" id="viewPlanBtn">My Plan</div>
    <div class="chip wide" id="viewBookingsBtn">My Bookings</div>
  </div>
</div>

<div class="section no-print">
  <div class="section-title">Live availability</div>
  <div class="live-status-line" id="liveStatus">Not logged in — showing total class capacity only (may be out of date).</div>
  <div class="live-error" id="liveErrorLine"></div>

  <div id="liveLoginFormWrap">
    <div class="live-disclaimer">
      Logging in fetches real-time spaces-left / waitlist numbers directly from Fitness First's member booking system, using your own account — this app never sees or stores your credentials on any server. If you check "remember me", your email and password are saved in this browser's local storage in plain text so you don't have to log in again — only do this on a device you trust, and log out on shared/public devices.
    </div>
    <form id="liveLoginForm">
      <div class="live-field">
        <label for="liveEmail">Email</label>
        <input type="email" id="liveEmail" autocomplete="username" required>
      </div>
      <div class="live-field">
        <label for="livePassword">Password</label>
        <input type="password" id="livePassword" autocomplete="current-password" required>
      </div>
      <div class="live-remember-row">
        <input type="checkbox" id="liveRemember" checked>
        <label for="liveRemember" style="margin:0;">Remember me on this device</label>
      </div>
      <button type="submit" class="live-btn" id="liveLoginBtn">Log in for live availability</button>
    </form>
  </div>

  <div id="liveLoggedInWrap" style="display:none;">
    <div class="live-loggedin-row">
      <span id="liveUpdatedText"></span>
      <span>
        <button class="live-secondary-btn" id="liveRefreshBtn">Refresh now</button>
        <button class="live-secondary-btn" id="liveLogoutBtn">Log out &amp; forget password</button>
      </span>
    </div>
    <div class="chip-wrap" style="margin-top:8px;">
      <div class="chip small" id="availOnlyToggle">Available to book only</div>
    </div>
  </div>
</div>

<div class="section" id="daySection">
  <div class="ms-header">
    <div class="section-title" style="margin-bottom:0;">Day</div>
    <span><span class="clear-link" id="daySelectAll">select all</span><span class="clear-link" id="dayClear">clear</span></span>
  </div>
  <div class="day-row" id="dayRow"></div>
</div>

<div class="section" id="todSection">
  <div class="section-title">Time of day</div>
  <div class="timeofday-grid" id="todGrid"></div>
</div>

<div class="section" id="moreFiltersSection">
  <div class="filter-toggle open" id="moreFiltersToggle">
    <div class="section-title" style="margin-bottom:0;">Center, type &amp; instructor</div>
    <span class="arrow">▾</span>
  </div>
  <div class="collapsible open" id="moreFiltersBody">
    <div class="ms-block">
      <div class="ms-header">
        <div class="section-title" style="margin-bottom:0;">Center</div>
        <span><span class="clear-link" id="centerSelectAll">select all</span><span class="clear-link" id="centerClear">clear</span></span>
      </div>
      <div class="chip-wrap" id="centerChips"></div>
    </div>
    <div class="ms-block">
      <div class="ms-header">
        <div class="section-title" style="margin-bottom:0;">Class type</div>
        <span class="clear-link" id="typeClear">clear</span>
      </div>
      <input type="text" class="ms-search" id="typeSearch" placeholder="Search class types...">
      <div class="chip-wrap scroll-box" id="typeChips"></div>
    </div>
    <div class="ms-block">
      <div class="ms-header">
        <div class="section-title" style="margin-bottom:0;">Instructor</div>
        <span><span class="clear-link" id="instructorSelectAll">select all</span><span class="clear-link" id="instructorClear">clear</span></span>
      </div>
      <input type="text" class="ms-search" id="instructorSearch" placeholder="Search instructors...">
      <div class="narrow-hint" id="instructorNarrowHint" style="display:none;"></div>
      <div class="chip-wrap scroll-box" id="instructorChips"></div>
    </div>
  </div>
  <div class="active-filters" id="activeFiltersLine" style="display:none;"></div>
</div>

<div id="listViewWrap">
  <div class="results-header">
    <div class="results-count" id="resultsCount">--</div>
    <select id="sortSelect" class="sort-select" style="width:auto;">
      <option value="time">Sort: time</option>
      <option value="outlet">Sort: center</option>
      <option value="class">Sort: class</option>
    </select>
  </div>
  <div id="resultsList"></div>
</div>

<div id="weekViewWrap" style="display:none;">
  <div class="results-header">
    <div class="results-count" id="weekResultsCount">--</div>
  </div>
  <div class="week-scroll">
    <table class="week-grid" id="weekGrid"></table>
  </div>
  <div class="week-hint">Scroll sideways for more days →</div>
</div>

<div id="planViewWrap" style="display:none;">
  <div class="section no-print" id="autoBookSection">
    <div class="section-title">Auto-book (6 days out)</div>
    <div class="live-status-line">At the exact time below, books everything in My Plan whose weekday is exactly 6 days from today — the day whose booking window opens at that moment. Requires live login, and this tab open and awake at trigger time. Re-arm manually each time you want it to run.</div>
    <div class="ab-row">
      <input type="number" id="abH" class="ab-time" min="0" max="23" value="18" style="width:52px;">
      <span class="ab-sep">:</span>
      <input type="number" id="abM" class="ab-time" min="0" max="59" value="0" style="width:52px;">
      <span class="ab-sep">:</span>
      <input type="number" id="abS" class="ab-time" min="0" max="59" value="0" style="width:52px;">
      <span class="ab-sep">.</span>
      <input type="number" id="abMs" class="ab-time" min="0" max="999" value="0" style="width:60px;">
      <button class="live-btn" id="autoBookArmBtn">Arm auto-book</button>
    </div>
    <div class="live-status-line" id="autoBookStatus"></div>
    <div id="autoBookPanel"></div>
  </div>

  <div class="print-title" id="printTitle"></div>
  <div class="results-header">
    <div class="results-count" id="planResultsCount">--</div>
    <div class="no-print" style="display:flex; gap:2px;">
      <span class="clear-link" id="planExportCsv">export csv</span>
      <span class="clear-link" id="planPrint">print</span>
      <span class="clear-link" id="planClear">clear plan</span>
    </div>
  </div>
  <div id="planList"></div>
</div>

<div id="bookingsViewWrap" style="display:none;">
  <div class="results-header">
    <div class="results-count" id="bookingsResultsCount">--</div>
    <span class="clear-link" id="bookingsRefresh">refresh</span>
  </div>
  <div id="bookingsList"></div>
</div>

<script>
const DATA = __DATA__;
const CAPACITY_LOOKUP = __CAPACITY_LOOKUP__;

const EXERP_BASE = 'https://fitnessfirst.exerp.site';
const EXERP_AUTH_URL = EXERP_BASE + '/api/user/authenticate';
const EXERP_SEARCH_URL = EXERP_BASE + '/api/classes/search-booking-participations';
const EXERP_CENTER_IDS = [110, 117, 109, 111, 121, 103, 105, 123, 108, 104, 124, 112, 118, 115];
const LIVE_CREDS_KEY = 'ff_live_creds_v1';

const DAYS = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
const TIME_BUCKETS = [
  {key:'early', label:'Early (5-9am)', start:5*60, end:9*60},
  {key:'morning', label:'Morning (9am-12pm)', start:9*60, end:12*60},
  {key:'midday', label:'Midday (12-2pm)', start:12*60, end:14*60},
  {key:'afternoon', label:'Afternoon (2-5pm)', start:14*60, end:17*60},
  {key:'evening', label:'Evening (5-8pm)', start:17*60, end:20*60},
  {key:'night', label:'Night (8pm+)', start:20*60, end:24*60},
];

function parseTimeToMinutes(t) {
  if (!t) return null;
  const m = t.trim().match(/^(\d{1,2}):(\d{2})(am|pm)$/i);
  if (!m) return null;
  let h = parseInt(m[1], 10);
  const min = parseInt(m[2], 10);
  const ap = m[3].toLowerCase();
  if (ap === 'pm' && h !== 12) h += 12;
  if (ap === 'am' && h === 12) h = 0;
  return h * 60 + min;
}

function planKey(d) {
  return [d.outlet, d.day, d.start, d.class, d.instructor].join('|');
}

DATA.forEach((d, i) => { d._startMin = parseTimeToMinutes(d.start); d.id = i; d.key = planKey(d); });

const jsDay = new Date().getDay(); // 0=Sun
let state = {
  view: 'list',
  days: new Set([DAYS[jsDay]]),
  timeBuckets: new Set(),
  centers: new Set(),
  types: new Set(),
  instructors: new Set(),
  plan: new Set(),
  sort: 'time',
  availableOnly: false,
  liveToken: null,
  liveMap: {},
  liveError: null,
  liveUpdatedAt: null,
  liveBusy: false,
  liveUserId: null,
  liveUserCenterId: null,
  bookingBusy: new Set(),
  bookedThisSession: new Set(),
  myBookings: [],
  myBookingsBusy: false,
  myBookingsError: null,
  myBookingsFetchedAt: null,
  cancelBusy: new Set(),
  autoBookArmed: false,
  autoBookTargetTime: null,
  autoBookResults: null,
  autoBookTimers: [],
};

const CENTER_COLORS = ['#f4c542','#38bdf8','#a78bfa','#34d399','#fb923c','#f472b6','#facc15','#4ade80','#60a5fa','#f87171','#c084fc','#2dd4bf','#fbbf24','#94a3b8'];

// ---- View toggle ----
const viewListBtn = document.getElementById('viewListBtn');
const viewWeekBtn = document.getElementById('viewWeekBtn');
const viewPlanBtn = document.getElementById('viewPlanBtn');
const viewBookingsBtn = document.getElementById('viewBookingsBtn');
const daySection = document.getElementById('daySection');
const todSection = document.getElementById('todSection');
const moreFiltersSection = document.getElementById('moreFiltersSection');
const listViewWrap = document.getElementById('listViewWrap');
const weekViewWrap = document.getElementById('weekViewWrap');
const planViewWrap = document.getElementById('planViewWrap');
const bookingsViewWrap = document.getElementById('bookingsViewWrap');

viewListBtn.onclick = () => { state.view = 'list'; render(); };
viewWeekBtn.onclick = () => { state.view = 'week'; render(); };
viewPlanBtn.onclick = () => { state.view = 'plan'; render(); };
viewBookingsBtn.onclick = () => { state.view = 'bookings'; render(); fetchMyBookings(); };
document.getElementById('bookingsRefresh').onclick = (e) => { e.stopPropagation(); fetchMyBookings(); };

// ---- My Plan: add/remove + persistence ----
// state.plan holds stable composite keys (outlet|day|start|class|instructor),
// not array indices — so saved picks still match up correctly after the
// weekly data refresh reshuffles DATA's order.
const PLAN_STORAGE_KEY = 'ff-my-plan-v2';

function togglePlan(key) {
  if (state.plan.has(key)) state.plan.delete(key);
  else state.plan.add(key);
  savePlan();
  render();
}

async function savePlan() {
  const value = JSON.stringify([...state.plan]);
  try {
    if (window.storage) {
      await window.storage.set(PLAN_STORAGE_KEY, value, false);
      return;
    }
  } catch (e) { /* fall through to localStorage */ }
  try {
    localStorage.setItem(PLAN_STORAGE_KEY, value);
  } catch (e) { /* best effort, not fatal */ }
}

async function loadPlan() {
  try {
    if (window.storage) {
      const res = await window.storage.get(PLAN_STORAGE_KEY, false);
      if (res && res.value) {
        JSON.parse(res.value).forEach(k => state.plan.add(k));
        render();
        return;
      }
    }
  } catch (e) { /* no saved plan yet via window.storage, try localStorage */ }
  try {
    const raw = localStorage.getItem(PLAN_STORAGE_KEY);
    if (raw) JSON.parse(raw).forEach(k => state.plan.add(k));
  } catch (e) { /* no saved plan yet, or storage unavailable */ }
  render();
}

document.getElementById('planClear').onclick = (e) => {
  e.stopPropagation();
  state.plan.clear();
  savePlan();
  render();
};

// ---- Export plan: CSV download + print ----
function csvEscape(val) {
  const s = String(val ?? '');
  if (/[",\n]/.test(s)) return '"' + s.replace(/"/g, '""') + '"';
  return s;
}

function getPlanSessionsSorted() {
  const dataByKey = {};
  DATA.forEach(d => { dataByKey[d.key] = d; });
  const sessions = [...state.plan].map(k => dataByKey[k]).filter(Boolean);
  const dayIndex = d => DAYS.indexOf(d.day);
  sessions.sort((a, b) => dayIndex(a) - dayIndex(b) || (a._startMin ?? 9999) - (b._startMin ?? 9999));
  return sessions;
}

function exportPlanCsv() {
  const sessions = getPlanSessionsSorted();
  const header = ['Day', 'Center', 'Class', 'Start', 'End', 'Instructor'];
  const rows = [header, ...sessions.map(s => [s.day, s.outlet, s.class, s.start || '', s.end || '', s.instructor || ''])];
  const csvText = rows.map(row => row.map(csvEscape).join(',')).join('\r\n');
  const blob = new Blob(['\ufeff' + csvText], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'my-fitness-plan.csv';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

document.getElementById('planExportCsv').onclick = (e) => { e.stopPropagation(); exportPlanCsv(); };
document.getElementById('autoBookArmBtn').onclick = () => {
  if (state.autoBookArmed) { disarmAutoBook(); } else { armAutoBook(); }
};
document.getElementById('planPrint').onclick = (e) => {
  e.stopPropagation();
  const today = new Date().toLocaleDateString('en-SG', { day: 'numeric', month: 'short', year: 'numeric' });
  document.getElementById('printTitle').innerHTML =
    `<div class="print-title">My Weekly Class Plan</div><div class="print-subtitle">Generated ${today}</div>`;
  window.print();
};

// ---- Day chips ----
const dayRow = document.getElementById('dayRow');
DAYS.forEach(d => {
  const chip = document.createElement('div');
  chip.className = 'chip' + (state.days.has(d) ? ' active' : '');
  chip.textContent = d;
  chip.dataset.day = d;
  chip.onclick = () => {
    if (state.days.has(d)) state.days.delete(d);
    else state.days.add(d);
    render();
  };
  dayRow.appendChild(chip);
});
document.getElementById('daySelectAll').onclick = (e) => { e.stopPropagation(); DAYS.forEach(d => state.days.add(d)); render(); };
document.getElementById('dayClear').onclick = (e) => { e.stopPropagation(); state.days.clear(); render(); };

// ---- Time-of-day chips (multi) ----
const todGrid = document.getElementById('todGrid');
TIME_BUCKETS.forEach(b => {
  const chip = document.createElement('div');
  chip.className = 'chip small';
  chip.textContent = b.label;
  chip.dataset.key = b.key;
  chip.onclick = () => {
    if (state.timeBuckets.has(b.key)) state.timeBuckets.delete(b.key);
    else state.timeBuckets.add(b.key);
    render();
  };
  todGrid.appendChild(chip);
});

// ---- Center / Type / Instructor multi-selects ----
const centers = [...new Set(DATA.map(d => d.outlet))].sort();
const types = [...new Set(DATA.map(d => d.class))].sort();
const instructors = [...new Set(DATA.map(d => d.instructor).filter(Boolean))].sort();

const centerColorMap = {};
centers.forEach((c, i) => { centerColorMap[c] = CENTER_COLORS[i % CENTER_COLORS.length]; });

function buildMultiSelect(containerEl, getValues, stateSet, searchInputEl) {
  let lastSearch = '';
  function renderChips(filterText) {
    if (filterText !== undefined) lastSearch = filterText;
    containerEl.innerHTML = '';
    const ft = (lastSearch || '').toLowerCase();
    const values = getValues();
    values.filter(v => v.toLowerCase().includes(ft)).forEach(v => {
      const chip = document.createElement('div');
      chip.className = 'chip small' + (stateSet.has(v) ? ' active' : '');
      chip.textContent = v;
      chip.dataset.value = v;
      chip.onclick = () => {
        if (stateSet.has(v)) stateSet.delete(v);
        else stateSet.add(v);
        render();
      };
      containerEl.appendChild(chip);
    });
  }
  renderChips('');
  if (searchInputEl) {
    searchInputEl.addEventListener('input', (e) => { renderChips(e.target.value); });
  }
  return renderChips;
}

const centerChipsEl = document.getElementById('centerChips');
const typeChipsEl = document.getElementById('typeChips');
const instructorChipsEl = document.getElementById('instructorChips');
const instructorNarrowHint = document.getElementById('instructorNarrowHint');

function getAvailableInstructors() {
  if (!state.types.size) return instructors;
  const allowed = new Set(DATA.filter(d => state.types.has(d.class)).map(d => d.instructor));
  return instructors.filter(i => allowed.has(i));
}

const renderCenterChips = buildMultiSelect(centerChipsEl, () => centers, state.centers, null);
const renderTypeChips = buildMultiSelect(typeChipsEl, () => types, state.types, document.getElementById('typeSearch'));
const renderInstructorChips = buildMultiSelect(instructorChipsEl, getAvailableInstructors, state.instructors, document.getElementById('instructorSearch'));

document.getElementById('centerClear').onclick = (e) => { e.stopPropagation(); state.centers.clear(); render(); };
document.getElementById('typeClear').onclick = (e) => { e.stopPropagation(); state.types.clear(); render(); };
document.getElementById('instructorClear').onclick = (e) => { e.stopPropagation(); state.instructors.clear(); render(); };

document.getElementById('centerSelectAll').onclick = (e) => {
  e.stopPropagation();
  [...centerChipsEl.children].forEach(c => state.centers.add(c.dataset.value));
  render();
};
document.getElementById('instructorSelectAll').onclick = (e) => {
  e.stopPropagation();
  [...instructorChipsEl.children].forEach(c => state.instructors.add(c.dataset.value));
  render();
};

// ---- More filters collapsible ----
const moreToggle = document.getElementById('moreFiltersToggle');
const moreBody = document.getElementById('moreFiltersBody');
moreToggle.onclick = () => {
  moreToggle.classList.toggle('open');
  moreBody.classList.toggle('open');
};

document.getElementById('sortSelect').onchange = (e) => { state.sort = e.target.value; render(); };

function formatActiveFilters() {
  const parts = [];
  if (state.centers.size) parts.push(state.centers.size + ' center' + (state.centers.size > 1 ? 's' : ''));
  if (state.types.size) parts.push(state.types.size + ' class type' + (state.types.size > 1 ? 's' : ''));
  if (state.instructors.size) parts.push(state.instructors.size + ' instructor' + (state.instructors.size > 1 ? 's' : ''));
  if (state.availableOnly) parts.push('available to book only');
  const line = document.getElementById('activeFiltersLine');
  if (parts.length) {
    line.style.display = 'block';
    line.innerHTML = 'Filtering: ' + parts.join(' · ') + ' <span class="clear-link" id="clearExtra">clear all</span>';
    document.getElementById('clearExtra').onclick = (e) => {
      e.stopPropagation();
      state.centers.clear();
      state.types.clear();
      state.instructors.clear();
      state.availableOnly = false;
      document.getElementById('availOnlyToggle').classList.remove('active');
      render();
    };
  } else {
    line.style.display = 'none';
  }
}

function matchesCommonFilters(d) {
  if (state.centers.size && !state.centers.has(d.outlet)) return false;
  if (state.types.size && !state.types.has(d.class)) return false;
  if (state.instructors.size && !state.instructors.has(d.instructor)) return false;
  if (state.timeBuckets.size) {
    if (d._startMin === null) return false;
    let ok = false;
    for (const key of state.timeBuckets) {
      const b = TIME_BUCKETS.find(x => x.key === key);
      if (d._startMin >= b.start && d._startMin < b.end) { ok = true; break; }
    }
    if (!ok) return false;
  }
  if (state.availableOnly && state.liveToken) {
    const key = dataRowKey(d);
    const live = key ? state.liveMap[key] : null;
    // No live match means we can't confirm it's bookable right now — leave it
    // out of "available only" rather than risk showing a full/waitlisted class.
    if (!live || live.spacesLeft <= 0) return false;
  }
  return true;
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function minutesToHHMM(min) {
  if (min === null || min === undefined) return null;
  const h = Math.floor(min / 60);
  const m = min % 60;
  return String(h).padStart(2, '0') + ':' + String(m).padStart(2, '0');
}

// The public schedule has no specific date, only a recurring weekday —
// so every lookup (static capacity, and live availability) is keyed by
// outlet + class + weekday + 24h start time, not by date or an ID.
// Fitness First's public site and its Exerp booking system don't always
// agree on outlet names (e.g. "One George Street" vs "George Street",
// "Tampines (CPF building)" vs "Tampines") — normalize before matching.
function normalizeOutlet(name) {
  return (name || '')
    .replace(/\s*\([^)]*\)\s*/g, ' ')
    .replace(/^\s*one\s+/i, '')
    .replace(/\s+/g, ' ')
    .trim()
    .toLowerCase();
}

function classKey(outlet, className, dayShort, hhmm24) {
  return [normalizeOutlet(outlet), className, dayShort, hhmm24].join('|');
}

function dataRowKey(d) {
  const hhmm = minutesToHHMM(d._startMin);
  if (!hhmm) return null;
  return classKey(d.outlet, d.class, d.day, hhmm);
}

function availabilityBadge(d) {
  const key = dataRowKey(d);
  const live = key ? state.liveMap[key] : null;
  if (live) {
    if (live.spacesLeft > 3) return `<span class="avail-badge avail-ok">${live.spacesLeft} left</span>`;
    if (live.spacesLeft > 0) return `<span class="avail-badge avail-low">${live.spacesLeft} left</span>`;
    if (live.waiting > 0) return `<span class="avail-badge avail-wait">Waitlist: ${live.waiting}</span>`;
    return `<span class="avail-badge avail-full">Full</span>`;
  }
  const cap = key ? CAPACITY_LOOKUP[key] : undefined;
  if (typeof cap === 'number') {
    return `<span class="avail-badge avail-cap">Cap ${cap}</span>`;
  }
  return '';
}

function sortResults(arr) {
  if (state.sort === 'time') {
    arr.sort((a,b) => (a._startMin ?? 9999) - (b._startMin ?? 9999));
  } else if (state.sort === 'outlet') {
    arr.sort((a,b) => a.outlet.localeCompare(b.outlet) || (a._startMin ?? 9999) - (b._startMin ?? 9999));
  } else if (state.sort === 'class') {
    arr.sort((a,b) => a.class.localeCompare(b.class) || (a._startMin ?? 9999) - (b._startMin ?? 9999));
  }
  return arr;
}

function buildClassCard(d) {
  const inPlan = state.plan.has(d.key);
  const card = document.createElement('div');
  card.className = 'class-card';
  card.innerHTML = `
      <div class="class-top">
        <div class="class-name">${escapeHtml(d.class)}</div>
        <div class="class-time">${d.start ? d.start + ' - ' + d.end : ''}</div>
      </div>
      <div class="class-meta">${escapeHtml(d.outlet)}${d.instructor ? ' · ' + escapeHtml(d.instructor) : ''}${availabilityBadge(d)}</div>
      <div style="margin-top:8px; display:flex; justify-content:flex-end;">
        <button class="plan-btn${inPlan ? ' in-plan' : ''}">${inPlan ? '✓ In plan' : '+ Add to plan'}</button>
        ${bookButtonHtml(d)}
      </div>
    `;
  card.querySelector('.plan-btn').addEventListener('click', () => togglePlan(d.key));
  attachBookHandler(card, d);
  return card;
}

function renderListView() {
  const dayFilterActive = state.days.size > 0;
  let results = DATA.filter(d => (!dayFilterActive || state.days.has(d.day)) && matchesCommonFilters(d));

  const distinctDays = [...new Set(results.map(r => r.day))];
  const list = document.getElementById('resultsList');
  list.innerHTML = '';

  if (results.length === 0) {
    document.getElementById('resultsCount').textContent = '0 classes';
    list.innerHTML = '<div class="empty-state"><div class="big">🧘</div>No classes match these filters.<br>Try widening your time range or day selection.</div>';
    return;
  }

  if (distinctDays.length <= 1) {
    sortResults(results);
    const dayLabel = distinctDays[0] || '';
    document.getElementById('resultsCount').textContent = results.length + (results.length === 1 ? ' class' : ' classes') + (dayLabel ? ' on ' + dayLabel : '');
    results.forEach(d => {
      list.appendChild(buildClassCard(d));
    });
  } else {
    document.getElementById('resultsCount').textContent = results.length + ' classes across ' + distinctDays.length + ' days';
    DAYS.filter(d => distinctDays.includes(d)).forEach(day => {
      const dayResults = sortResults(results.filter(r => r.day === day));
      const header = document.createElement('div');
      header.className = 'day-group-header';
      header.textContent = day + ' · ' + dayResults.length + (dayResults.length === 1 ? ' class' : ' classes');
      list.appendChild(header);
      dayResults.forEach(d => {
        list.appendChild(buildClassCard(d));
      });
    });
  }
}

function renderWeekView() {
  // Weekly schedule always shows the full week — the "List by day" day
  // chips are a List-view-only filter and intentionally don't carry over.
  const columns = DAYS;
  const results = DATA.filter(d => matchesCommonFilters(d));

  document.getElementById('weekResultsCount').textContent = results.length + (results.length === 1 ? ' class' : ' classes') + ' this week';

  const grid = document.getElementById('weekGrid');
  grid.innerHTML = '';

  if (results.length === 0) {
    grid.style.display = 'none';
    let empty = document.getElementById('weekEmptyState');
    if (!empty) {
      empty = document.createElement('div');
      empty.id = 'weekEmptyState';
      empty.className = 'empty-state';
      empty.innerHTML = '<div class="big">🧘</div>No classes match these filters.<br>Try widening your time range, or pick fewer instructors/types.';
      grid.parentElement.appendChild(empty);
    }
    empty.style.display = 'block';
    return;
  } else {
    grid.style.display = 'table';
    const empty = document.getElementById('weekEmptyState');
    if (empty) empty.style.display = 'none';
  }

  // rows = centers that have at least one matching session, sorted alphabetically
  const centersWithResults = [...new Set(results.map(r => r.outlet))].sort();

  // group results by outlet + day
  const byOutletDay = {};
  results.forEach(r => {
    const key = r.outlet + '|' + r.day;
    if (!byOutletDay[key]) byOutletDay[key] = [];
    byOutletDay[key].push(r);
  });
  Object.values(byOutletDay).forEach(arr => arr.sort((a,b) => (a._startMin ?? 9999) - (b._startMin ?? 9999)));

  // header row
  const thead = document.createElement('thead');
  const headRow = document.createElement('tr');
  const cornerTh = document.createElement('th');
  cornerTh.className = 'center-col';
  cornerTh.textContent = 'Center';
  headRow.appendChild(cornerTh);
  DAYS.filter(d => columns.includes(d)).forEach(d => {
    const th = document.createElement('th');
    th.textContent = d;
    headRow.appendChild(th);
  });
  thead.appendChild(headRow);
  grid.appendChild(thead);

  const tbody = document.createElement('tbody');
  centersWithResults.forEach(outlet => {
    const tr = document.createElement('tr');
    const nameTd = document.createElement('td');
    nameTd.className = 'center-col';
    nameTd.textContent = outlet;
    tr.appendChild(nameTd);
    columns.forEach(day => {
      const td = document.createElement('td');
      const key = outlet + '|' + day;
      const sessions = byOutletDay[key];
      if (sessions && sessions.length) {
        sessions.forEach(s => {
          const slot = document.createElement('div');
          const inPlan = state.plan.has(s.key);
          slot.className = 'week-slot';
          slot.innerHTML = `<span class="t">${s.start ? s.start + '-' + s.end : ''}</span><span class="c">${escapeHtml(s.class)}${availabilityBadge(s)}</span>${s.instructor ? '<span class="i">' + escapeHtml(s.instructor) + '</span>' : ''}<button class="plan-btn${inPlan ? ' in-plan' : ''}">${inPlan ? '✓' : '+ plan'}</button>${bookButtonHtml(s)}`;
          slot.querySelector('.plan-btn').addEventListener('click', () => togglePlan(s.key));
          attachBookHandler(slot, s);
          td.appendChild(slot);
        });
      }
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
  grid.appendChild(tbody);
}

function renderPlanView() {
  const dataByKey = {};
  DATA.forEach(d => { dataByKey[d.key] = d; });
  const sessions = [...state.plan].map(k => dataByKey[k]).filter(Boolean);
  const list = document.getElementById('planList');
  list.innerHTML = '';

  document.getElementById('planResultsCount').textContent = sessions.length + (sessions.length === 1 ? ' class in your plan' : ' classes in your plan');

  if (sessions.length === 0) {
    list.innerHTML = '<div class="empty-state"><div class="big">📋</div>Your plan is empty.<br>Browse "List by day" or "Weekly schedule" and tap <b>+ Add to plan</b> on any class.</div>';
    return;
  }

  const byDay = {};
  sessions.forEach(s => { (byDay[s.day] = byDay[s.day] || []).push(s); });

  DAYS.filter(d => byDay[d]).forEach(day => {
    const dayHeader = document.createElement('div');
    dayHeader.className = 'plan-day-header';
    dayHeader.textContent = day;
    list.appendChild(dayHeader);

    const byCenter = {};
    byDay[day].forEach(s => { (byCenter[s.outlet] = byCenter[s.outlet] || []).push(s); });

    Object.keys(byCenter).sort().forEach(outlet => {
      const centerHeader = document.createElement('div');
      centerHeader.className = 'plan-center-header';
      centerHeader.style.background = centerColorMap[outlet] || '#8a91a3';
      centerHeader.textContent = outlet;
      list.appendChild(centerHeader);

      const rows = sortResults(byCenter[outlet].slice());
      rows.forEach(s => {
        const row = document.createElement('div');
        row.className = 'plan-session-row';
        row.innerHTML = `
          <div class="plan-session-info">
            <span class="t">${s.start ? s.start + '-' + s.end : ''}</span><span class="c">${escapeHtml(s.class)}${availabilityBadge(s)}</span>
            ${s.instructor ? '<span class="i">' + escapeHtml(s.instructor) + '</span>' : ''}
          </div>
          <div class="plan-remove">✕</div>
        `;
        row.querySelector('.plan-remove').addEventListener('click', () => togglePlan(s.key));
        list.appendChild(row);
      });
    });
  });
}

function render() {
  // view toggle visuals
  viewListBtn.classList.toggle('active', state.view === 'list');
  viewWeekBtn.classList.toggle('active', state.view === 'week');
  viewPlanBtn.classList.toggle('active', state.view === 'plan');
  viewBookingsBtn.classList.toggle('active', state.view === 'bookings');
  daySection.style.display = state.view === 'list' ? 'block' : 'none';
  todSection.style.display = (state.view === 'plan' || state.view === 'bookings') ? 'none' : 'block';
  moreFiltersSection.style.display = (state.view === 'plan' || state.view === 'bookings') ? 'none' : 'block';
  listViewWrap.style.display = state.view === 'list' ? 'block' : 'none';
  weekViewWrap.style.display = state.view === 'week' ? 'block' : 'none';
  planViewWrap.style.display = state.view === 'plan' ? 'block' : 'none';
  bookingsViewWrap.style.display = state.view === 'bookings' ? 'block' : 'none';
  renderAutoBookStatus();
  renderAutoBookPanel();

  // day chips active state
  [...dayRow.children].forEach(c => c.classList.toggle('active', state.days.has(c.dataset.day)));
  // time bucket chips
  [...todGrid.children].forEach(c => c.classList.toggle('active', state.timeBuckets.has(c.dataset.key)));

  // narrow instructor list by selected class type(s); drop any selections no longer valid
  const availableInstructors = getAvailableInstructors();
  const availableSet = new Set(availableInstructors);
  [...state.instructors].forEach(i => { if (!availableSet.has(i)) state.instructors.delete(i); });
  instructorNarrowHint.style.display = state.types.size ? 'block' : 'none';
  if (state.types.size) {
    instructorNarrowHint.textContent = 'Showing instructors who teach ' + [...state.types].join(', ');
  }
  renderInstructorChips();

  // re-render chips (rebuilds DOM, so do this before toggling active classes on them)
  [...centerChipsEl.children].forEach(c => c.classList.toggle('active', state.centers.has(c.dataset.value)));
  [...typeChipsEl.children].forEach(c => c.classList.toggle('active', state.types.has(c.dataset.value)));
  [...instructorChipsEl.children].forEach(c => c.classList.toggle('active', state.instructors.has(c.dataset.value)));

  formatActiveFilters();

  if (state.view === 'list') {
    renderListView();
  } else if (state.view === 'week') {
    renderWeekView();
  } else if (state.view === 'bookings') {
    renderBookingsView();
  } else {
    renderPlanView();
  }
}

// ---- Live availability (client-side login + fetch, optional) ----
function saveLiveCreds(email, password) {
  try {
    localStorage.setItem(LIVE_CREDS_KEY, JSON.stringify({ email, password }));
  } catch (e) { /* best effort */ }
}
function loadLiveCreds() {
  try {
    const raw = localStorage.getItem(LIVE_CREDS_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch (e) { return null; }
}
function clearLiveCreds() {
  try { localStorage.removeItem(LIVE_CREDS_KEY); } catch (e) { /* best effort */ }
}

async function liveLogin(email, password) {
  state.liveError = null;
  try {
    const resp = await fetch(EXERP_AUTH_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, sessionTimeoutOneMonth: false }),
    });
    if (!resp.ok) throw new Error('login rejected (HTTP ' + resp.status + ') — check email/password');
    const data = await resp.json();
    if (!data.token) throw new Error('no token in login response');
    state.liveToken = data.token;
    state.liveUserId = data.user ? data.user.userId : null;
    state.liveUserCenterId = data.user ? data.user.centerId : null;
    return true;
  } catch (e) {
    state.liveToken = null;
    state.liveUserId = null;
    state.liveUserCenterId = null;
    state.liveError = 'Live login failed: ' + e.message + '. This can also happen if Fitness First blocks browser-based requests to this endpoint — the scraper-based capacity numbers still work either way.';
    return false;
  }
}

function todayPlusDays(n) {
  const d = new Date();
  d.setDate(d.getDate() + n);
  return d;
}

function isoDate(d) {
  return d.toISOString().slice(0, 10);
}

async function fetchLiveAvailability() {
  if (!state.liveToken) return;
  state.liveBusy = true;
  const newMap = {};
  let anyError = null;
  for (let i = 0; i < 7; i++) {
    const dateObj = todayPlusDays(i);
    const date = isoDate(dateObj);
    const dayShort = DAYS[dateObj.getDay()];
    try {
      const resp = await fetch(EXERP_SEARCH_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + state.liveToken,
        },
        body: JSON.stringify({
          activityGroupIds: [],
          activityIds: [],
          centers: EXERP_CENTER_IDS,
          dateFrom: date,
          dateTo: date,
        }),
      });
      if (!resp.ok) throw new Error('HTTP ' + resp.status);
      const items = await resp.json();
      items.forEach(item => {
        const b = item.booking;
        if (!b) return;
        const capacity = b.classCapacity ?? 0;
        const booked = b.bookedCount ?? 0;
        const rec = {
          spacesLeft: Math.max(capacity - booked, 0),
          waiting: b.waitingListCount ?? 0,
          capacity, booked,
          bookingId: b.id,
          bookingCenterId: item.centerId,
        };
        const key = classKey(item.centerName || '', b.name || '', dayShort, b.startTime || '');
        newMap[key] = rec;
      });
    } catch (e) {
      anyError = e;
    }
  }
  state.liveMap = newMap;
  state.liveUpdatedAt = new Date();
  state.liveBusy = false;
  if (anyError) {
    state.liveError = 'Some live data failed to refresh (' + anyError.message + '); showing what loaded.';
  }
  render();
}

// ---- Booking (live login required) ----
function nextOccurrenceDateTime(d) {
  for (let i = 0; i < 7; i++) {
    const dt = todayPlusDays(i);
    if (DAYS[dt.getDay()] === d.day) {
      const startMin = d._startMin ?? 0;
      dt.setHours(Math.floor(startMin / 60), startMin % 60, 0, 0);
      return dt;
    }
  }
  return null;
}

function hoursUntilClass(d) {
  const dt = nextOccurrenceDateTime(d);
  if (!dt) return Infinity;
  return (dt - new Date()) / 3600000;
}

// Core booking call — no confirm dialog, no alert. Returns a result object
// so both the interactive Book button and the silent auto-book batch can
// use the same logic and present it their own way.
async function doBookRequest(d, live) {
  const key = dataRowKey(d);
  state.bookingBusy.add(key);
  render();
  try {
    const resp = await fetch(EXERP_BASE + '/api/booking/create-booking', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + state.liveToken,
      },
      body: JSON.stringify({
        selectedUserId: state.liveUserId,
        selectedUserCenterId: state.liveUserCenterId,
        bookingCenterId: live.bookingCenterId,
        bookingId: live.bookingId,
      }),
    });
    if (!resp.ok) {
      const text = await resp.text().catch(() => '');
      throw new Error('HTTP ' + resp.status + (text ? ': ' + text.slice(0, 200) : ''));
    }
    const result = await resp.json();
    if (result.state && result.state !== 'BOOKED') {
      throw new Error('Unexpected response state: ' + result.state);
    }
    state.bookedThisSession.add(key);
    return { status: 'booked', message: `Booked: ${d.class} at ${d.outlet}, ${d.day} ${d.start}.` };
  } catch (e) {
    return { status: 'error', message: 'Booking failed: ' + e.message };
  } finally {
    state.bookingBusy.delete(key);
    render();
  }
}

// Interactive Book button handler. No confirmation needed unless the class
// starts within 2 hours, in which case we ask once before firing.
async function bookClass(d) {
  const key = dataRowKey(d);
  const live = key ? state.liveMap[key] : null;
  if (!live || !live.bookingId || !live.bookingCenterId) {
    alert("Can't book this class right now — no live session data for it. Try Refresh, or it may be outside the next 7 days.");
    return;
  }
  if (!state.liveUserId || !state.liveUserCenterId) {
    alert('Missing your member ID from login — try logging out and back in.');
    return;
  }
  if (hoursUntilClass(d) < 2) {
    const confirmMsg = `${d.class} at ${d.outlet} starts in under 2 hours (${d.day} ${d.start}). Book anyway?`;
    if (!confirm(confirmMsg)) return;
  }
  const result = await doBookRequest(d, live);
  alert(result.message);
  await fetchLiveAvailability();
}

function bookButtonHtml(d) {
  if (!state.liveToken) return '';
  const key = dataRowKey(d);
  if (!key) return '';
  const live = state.liveMap[key];
  if (!live || !live.bookingId) return '';
  if (state.bookedThisSession.has(key)) {
    return '<button class="book-btn booked" disabled>\u2713 Booked</button>';
  }
  if (state.bookingBusy.has(key)) {
    return '<button class="book-btn" disabled>Booking\u2026</button>';
  }
  if (live.spacesLeft <= 0 && live.waiting <= 0) {
    return '<button class="book-btn" disabled>Full</button>';
  }
  const label = live.spacesLeft > 0 ? 'Book' : 'Join waitlist';
  return `<button class="book-btn" data-key="${escapeHtml(key)}">${label}</button>`;
}

function attachBookHandler(container, d) {
  const btn = container.querySelector('.book-btn:not([disabled])');
  if (btn) btn.addEventListener('click', () => bookClass(d));
}

// ---- My Bookings (live login required) ----
function bookingDateTime(b) {
  return new Date(b.date + 'T' + b.startTime + ':00');
}

async function fetchMyBookings() {
  if (!state.liveToken || !state.liveUserId || !state.liveUserCenterId) {
    state.myBookingsError = 'Log in above to see your bookings.';
    state.myBookings = [];
    render();
    return;
  }
  state.myBookingsBusy = true;
  state.myBookingsError = null;
  render();
  try {
    const resp = await fetch(EXERP_BASE + '/api/dashboard/schedule-by-current-person', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + state.liveToken,
      },
      body: JSON.stringify({
        selectedUserId: state.liveUserId,
        selectedUserCenterId: state.liveUserCenterId,
        listOfActivities: [],
        selectAllMembers: false,
      }),
    });
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    const items = await resp.json();
    const now = new Date();
    const upcoming = items.filter(item => {
      const b = item.booking;
      return b && item.state === 'BOOKED' && bookingDateTime(b) >= now;
    });
    upcoming.sort((a, b) => bookingDateTime(a.booking) - bookingDateTime(b.booking));
    state.myBookings = upcoming;
  } catch (e) {
    state.myBookingsError = 'Failed to load bookings: ' + e.message;
  } finally {
    state.myBookingsBusy = false;
    state.myBookingsFetchedAt = new Date();
    render();
  }
}

async function cancelBooking(item) {
  const b = item.booking;
  const dt = bookingDateTime(b);
  const hoursUntil = (dt - new Date()) / 3600000;
  if (hoursUntil < 2) {
    const confirmMsg = `Cancel ${b.name} at ${item.centerName}, ${b.date} ${b.startTime}?\n\n\u26A0 This is within 2 hours of the class \u2014 cancelling now may count as a late cancel toward your 30-day no-show/late-cancel limit.`;
    if (!confirm(confirmMsg)) return;
  }

  state.cancelBusy.add(item.id);
  render();
  try {
    const resp = await fetch(EXERP_BASE + '/api/booking/cancel-booking', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + state.liveToken,
      },
      body: JSON.stringify({
        selectedUserId: state.liveUserId,
        selectedUserCenterId: state.liveUserCenterId,
        participationCenterId: item.centerId,
        participationId: item.id,
      }),
    });
    if (!resp.ok) {
      const text = await resp.text().catch(() => '');
      throw new Error('HTTP ' + resp.status + (text ? ': ' + text.slice(0, 200) : ''));
    }
    state.myBookings = state.myBookings.filter(x => x.id !== item.id);
    await fetchLiveAvailability();
  } catch (e) {
    alert('Cancel failed: ' + e.message);
  } finally {
    state.cancelBusy.delete(item.id);
    render();
  }
}

function renderBookingsView() {
  const list = document.getElementById('bookingsList');
  list.innerHTML = '';

  if (!state.liveToken) {
    document.getElementById('bookingsResultsCount').textContent = '--';
    list.innerHTML = '<div class="empty-state"><div class="big">\uD83D\uDD12</div>Log in under "Live availability" above to see your upcoming bookings.</div>';
    return;
  }

  if (state.myBookingsBusy && state.myBookings.length === 0) {
    document.getElementById('bookingsResultsCount').textContent = 'Loading\u2026';
    return;
  }

  if (state.myBookingsError) {
    document.getElementById('bookingsResultsCount').textContent = '--';
    list.innerHTML = `<div class="empty-state"><div class="big">\u26A0</div>${escapeHtml(state.myBookingsError)}</div>`;
    return;
  }

  document.getElementById('bookingsResultsCount').textContent =
    state.myBookings.length + (state.myBookings.length === 1 ? ' upcoming booking' : ' upcoming bookings');

  if (state.myBookings.length === 0) {
    list.innerHTML = '<div class="empty-state"><div class="big">\uD83D\uDCC5</div>No upcoming bookings found.</div>';
    return;
  }

  state.myBookings.forEach(item => {
    const b = item.booking;
    const instructors = (b.instructorNames || []).map(n => n.replace(/\s*\.\s*$/, '')).join(', ');
    const hoursUntil = (bookingDateTime(b) - new Date()) / 3600000;
    const row = document.createElement('div');
    row.className = 'class-card';
    const busy = state.cancelBusy.has(item.id);
    row.innerHTML = `
      <div class="class-top">
        <div class="class-name">${escapeHtml(b.name)}</div>
        <div class="class-time">${b.startTime}-${b.endTime}</div>
      </div>
      <div class="class-meta">${escapeHtml(item.centerName)} \u00b7 ${escapeHtml(b.date)}${instructors ? ' \u00b7 ' + escapeHtml(instructors) : ''}</div>
      ${hoursUntil < 2 ? '<div class="live-error" style="display:block; margin-top:6px;">Within 2 hours \u2014 cancelling now may count as a late cancel.</div>' : ''}
      <div style="margin-top:8px; display:flex; justify-content:flex-end;">
        <button class="book-btn" ${busy ? 'disabled' : ''}>${busy ? 'Cancelling\u2026' : 'Cancel'}</button>
      </div>
    `;
    if (!busy) {
      row.querySelector('.book-btn').addEventListener('click', () => cancelBooking(item));
    }
    list.appendChild(row);
  });
}

// ---- Auto-book: fire everything in My Plan for the weekday that's
// exactly 6 days out, at a precise time. Manual arm each time by design. ----
function computeEligibleDay() {
  return DAYS[todayPlusDays(6).getDay()];
}

function getPlanRows() {
  return DATA.filter(d => state.plan.has(d.key));
}

function clearAutoBookTimers() {
  state.autoBookTimers.forEach(t => clearTimeout(t));
  state.autoBookTimers = [];
}

function armAutoBook() {
  const h = parseInt(document.getElementById('abH').value, 10) || 0;
  const m = parseInt(document.getElementById('abM').value, 10) || 0;
  const s = parseInt(document.getElementById('abS').value, 10) || 0;
  const ms = parseInt(document.getElementById('abMs').value, 10) || 0;
  const target = new Date();
  target.setHours(h, m, s, ms);
  if (target <= new Date()) {
    alert('That time has already passed today. Pick a future time.');
    return;
  }
  if (!state.liveToken) {
    alert('Log in under "Live availability" first \u2014 auto-book needs an active session.');
    return;
  }
  state.autoBookArmed = true;
  state.autoBookTargetTime = target;
  state.autoBookResults = null;
  clearAutoBookTimers();

  const msUntilTarget = target - new Date();
  const preFetchDelay = Math.max(msUntilTarget - 5000, 0);
  const t1 = setTimeout(() => { fetchLiveAvailability(); }, preFetchDelay);
  const t2 = setTimeout(() => { runAutoBook(); }, msUntilTarget);
  state.autoBookTimers = [t1, t2];
  render();
}

function disarmAutoBook() {
  clearAutoBookTimers();
  state.autoBookArmed = false;
  state.autoBookTargetTime = null;
  render();
}

async function runAutoBook() {
  state.autoBookArmed = false;
  const eligibleDay = computeEligibleDay();
  const planRows = getPlanRows();
  const results = [];
  const toFire = [];

  planRows.forEach(d => {
    if (d.day !== eligibleDay) {
      results.push({ d, status: 'skip', message: `Not today's 6-day-out day (this is ${d.day}, today opens ${eligibleDay})` });
      return;
    }
    const key = dataRowKey(d);
    const live = key ? state.liveMap[key] : null;
    if (!live || !live.bookingId || !live.bookingCenterId) {
      results.push({ d, status: 'skip', message: 'No live match for this class (booking window may not be open yet, or center name mismatch)' });
      return;
    }
    if (live.spacesLeft <= 0 && live.waiting <= 0) {
      results.push({ d, status: 'fail', message: 'Full, no waitlist available' });
      return;
    }
    toFire.push({ d, live });
  });

  // Safety net matching manual-booking rules: confirm individually if a
  // class somehow starts within 2 hours (should never happen 6 days out).
  const immediate = [];
  for (const { d, live } of toFire) {
    if (hoursUntilClass(d) < 2) {
      const ok = confirm(`${d.class} at ${d.outlet} starts in under 2 hours. Book anyway?`);
      if (!ok) {
        results.push({ d, status: 'skip', message: 'Skipped \u2014 under 2 hours, not confirmed' });
        continue;
      }
    }
    immediate.push({ d, live });
  }

  const outcomes = await Promise.allSettled(immediate.map(({ d, live }) => doBookRequest(d, live)));
  outcomes.forEach((outcome, i) => {
    const { d } = immediate[i];
    if (outcome.status === 'fulfilled') {
      results.push({ d, status: outcome.value.status === 'booked' ? 'ok' : 'fail', message: outcome.value.message });
    } else {
      results.push({ d, status: 'fail', message: 'Booking failed: ' + outcome.reason });
    }
  });

  state.autoBookResults = results;
  await fetchLiveAvailability();
  render();
}

function renderAutoBookStatus() {
  const statusEl = document.getElementById('autoBookStatus');
  const btn = document.getElementById('autoBookArmBtn');
  if (!statusEl || !btn) return;
  if (state.autoBookArmed && state.autoBookTargetTime) {
    const t = state.autoBookTargetTime;
    const hh = String(t.getHours()).padStart(2, '0');
    const mm = String(t.getMinutes()).padStart(2, '0');
    const ss = String(t.getSeconds()).padStart(2, '0');
    const mmm = String(t.getMilliseconds()).padStart(3, '0');
    statusEl.textContent = `Armed \u2014 will fire at ${hh}:${mm}:${ss}.${mmm} for ${computeEligibleDay()} classes in My Plan. Keep this tab open and awake.`;
    btn.textContent = 'Disarm';
  } else {
    statusEl.textContent = '';
    btn.textContent = 'Arm auto-book';
  }
}

function renderAutoBookPanel() {
  const panel = document.getElementById('autoBookPanel');
  if (!panel) return;
  if (!state.autoBookResults) { panel.innerHTML = ''; return; }
  panel.innerHTML = state.autoBookResults.map(r => {
    const cls = r.status === 'ok' ? 'ok' : (r.status === 'fail' ? 'fail' : 'skip');
    const tag = r.status === 'ok' ? '\u2713 Booked' : (r.status === 'fail' ? '\u2717 Failed' : '\u2014 Skipped');
    return `<div class="ab-result-row ${cls}"><span>${escapeHtml(r.d.class)} \u00b7 ${escapeHtml(r.d.outlet)} \u00b7 ${r.d.day} ${r.d.start}</span><span class="ab-status-tag">${tag}</span></div>` +
      `<div style="font-size:11px; color:var(--muted); margin:-4px 0 6px 4px;">${escapeHtml(r.message)}</div>`;
  }).join('');
}

function renderLiveStatus() {
  const statusEl = document.getElementById('liveStatus');
  const errEl = document.getElementById('liveErrorLine');
  const formWrap = document.getElementById('liveLoginFormWrap');
  const loggedInWrap = document.getElementById('liveLoggedInWrap');

  if (state.liveToken) {
    formWrap.style.display = 'none';
    loggedInWrap.style.display = 'block';
    statusEl.style.display = 'none';
    document.getElementById('liveUpdatedText').textContent = state.liveBusy
      ? 'Refreshing live availability…'
      : (state.liveUpdatedAt ? 'Live availability updated ' + state.liveUpdatedAt.toLocaleTimeString() : 'Logged in.');
  } else {
    formWrap.style.display = 'block';
    loggedInWrap.style.display = 'none';
    statusEl.style.display = 'block';
    statusEl.textContent = 'Not logged in — showing total class capacity only (may be out of date).';
    // Without a live session there's no spaces-left/waitlist signal to filter
    // on, so drop back to showing everything.
    state.availableOnly = false;
  }
  document.getElementById('availOnlyToggle').classList.toggle('active', state.availableOnly);

  if (state.liveError) {
    errEl.textContent = state.liveError;
    errEl.style.display = 'block';
  } else {
    errEl.style.display = 'none';
  }
}

document.getElementById('liveLoginForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const email = document.getElementById('liveEmail').value.trim();
  const password = document.getElementById('livePassword').value;
  const remember = document.getElementById('liveRemember').checked;
  const btn = document.getElementById('liveLoginBtn');
  btn.disabled = true;
  btn.textContent = 'Logging in…';
  const ok = await liveLogin(email, password);
  if (ok) {
    if (remember) saveLiveCreds(email, password);
    else clearLiveCreds();
    renderLiveStatus();
    await fetchLiveAvailability();
  }
  btn.disabled = false;
  btn.textContent = 'Log in for live availability';
  renderLiveStatus();
  render();
});

document.getElementById('availOnlyToggle').onclick = (e) => {
  state.availableOnly = !state.availableOnly;
  e.currentTarget.classList.toggle('active', state.availableOnly);
  render();
};

document.getElementById('liveRefreshBtn').onclick = async () => {
  renderLiveStatus();
  await fetchLiveAvailability();
  renderLiveStatus();
};

document.getElementById('liveLogoutBtn').onclick = () => {
  state.liveToken = null;
  state.liveMap = {};
  state.liveError = null;
  state.liveUpdatedAt = null;
  state.liveUserId = null;
  state.liveUserCenterId = null;
  state.bookedThisSession = new Set();
  state.myBookings = [];
  state.myBookingsError = null;
  state.myBookingsFetchedAt = null;
  clearLiveCreds();
  document.getElementById('liveEmail').value = '';
  document.getElementById('livePassword').value = '';
  renderLiveStatus();
  render();
};

async function initLive() {
  const creds = loadLiveCreds();
  if (creds && creds.email && creds.password) {
    document.getElementById('liveEmail').value = creds.email;
    document.getElementById('liveRemember').checked = true;
    const ok = await liveLogin(creds.email, creds.password);
    renderLiveStatus();
    if (ok) await fetchLiveAvailability();
  }
  renderLiveStatus();
  render();
}

render();
loadPlan();
initLive();
</script>
</body>
</html>
"""

import datetime
build_date = datetime.date.today().strftime("%d %b %Y")
html = html.replace("__DATA__", data_json)
html = html.replace("__CAPACITY_LOOKUP__", capacity_lookup_json)
html = html.replace("__BUILD_DATE__", build_date)

out_path = script_dir / 'docs' / 'index.html'
out_path.parent.mkdir(exist_ok=True)
with open(out_path, 'w') as f:
    f.write(html)

print(f"written {len(html)} bytes to {out_path}", file=sys.stderr)
