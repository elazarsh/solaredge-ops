# solaredge-ops

Custom fleet monitoring, alerting, and reporting for SolarEdge PV installations,
built on top of the [SolarEdge Monitoring API](https://monitoringapi.solaredge.com).

SolarEdge's own portal covers a lot of ground (scheduled monthly summary emails,
"Alert Profiles" with app push), but it has two hard gaps that this tool fills:

- **No way to route different people to different alerts** — e.g. the maintenance
  crew needs real-time field issues, finance only cares about the monthly
  production/financial summary, and management wants just the critical headlines —
  and no way to define your own cross-site rules (e.g. "this site is
  underperforming relative to the rest of the fleet").
- **The public API exposes no alert/fault-event endpoint and no webhooks** — so any
  custom alerting has to be derived locally from the same raw metrics
  (`overview`, `details`, `power`, `energy`) that the portal itself uses.

`solaredge-ops` polls those metrics on a schedule, evaluates a small rule engine
against them, deduplicates findings against local state (so you're notified once
per problem — not every 30 minutes while it persists), and routes each alert to
the people who actually want to hear about it, on the channel(s) that reach them
(Telegram and/or email — see [Recipients & routing](#recipients--routing) below).
It also generates the monthly production report by computing it directly from
the `energy` endpoint, so the report's content and audience are entirely under
your control.

It is intentionally a "do one pass and exit" CLI rather than a long-running daemon
— cron / systemd timers / Task Scheduler are simpler to operate, monitor, and
restart than a Python process that has to stay up forever.

## How it works

```
solaredge-ops check   →  fetch site overview+details
                       →  evaluate alert rules against the snapshot(s)
                       →  de-duplicate against SQLite state (only notify on change)
                       →  route new alerts / resolutions to subscribed recipients

solaredge-ops report  →  pull last month's daily energy per site
                       →  build an HTML/text summary (vs. previous month, vs. baseline)
                       →  email it to whoever opted into "monthly_report"

solaredge-ops contacts →  list configured recipients and what each is subscribed to

solaredge-ops quota   →  show the local estimate of remaining daily API requests
```

## Alert rules

All rules are independently enabled/configured in `config.yaml`:

| Rule | Fires when |
|---|---|
| `equipment_offline` | A site hasn't reported fresh data for `grace_minutes` |
| `zero_production_daylight` | A site is reporting, it's the middle of the day, but power output is ~0 |
| `low_production` | Today's energy-so-far is below a time-adjusted fraction of `expected_daily_kwh` |
| `performance_drop` | A site's normalized output (power / peak power) is far below the fleet median (needs ≥3 reporting sites) |
| `alert_count_jump` | SolarEdge's own per-site `alertQuantity` counter increases since the last check |

Each rule produces `Alert` objects with a `dedup_key`; the local `StateStore`
(SQLite) tracks which problems are currently "open" so you get exactly one
notification when a problem starts and one "resolved" message when it clears —
no repeated spam every polling cycle.

## Recipients & routing

Different people on your team need very different things from this system —
e.g.:

- **Maintenance/cleaning crew** — real-time, actionable field issues
  (equipment offline, zero/low production, performance drops) so they can
  drive out and fix it. Best delivered as an instant Telegram push to a group.
- **Finance** — not interested in every blip; cares about the periodic
  production/financial summary (the monthly report). Best delivered by email.
- **Management** — wants the big picture without the noise: only the
  most critical issues, plus the monthly summary.

`solaredge-ops` models this directly with a `recipients` directory in
`config.yaml` — no separate UI or database needed, since the config file
already has to be edited to add a site or tune a threshold. Each entry
declares:

- **how to reach them** — `telegram_chat_id` and/or `email` (at least one is
  required); `phone` is also stored as part of the team directory for your own
  reference (there's no SMS channel yet, so it isn't used for delivery)
- **what they're subscribed to** — `categories`: a list of alert rule names,
  the wildcard `all`, and/or the special pseudo-category `monthly_report`
  (opt-in only — `all` does *not* imply the report, so nobody gets an email
  they didn't ask for)
- **how urgent it has to be** — `min_severity`: `info` / `warning` / `critical`;
  anything below this floor is silently skipped for that person

```yaml
recipients:
  - name: "Danny - Maintenance lead"
    role: maintenance
    phone: "+972-50-000-0000"
    telegram_chat_id: "-1001234567890"   # the crew's group chat
    categories: [equipment_offline, zero_production_daylight, low_production, performance_drop, alert_count_jump]
    min_severity: warning

  - name: "Ronit - Finance"
    role: finance
    email: "ronit@example.com"
    categories: [monthly_report]

  - name: "Yossi - CEO"
    role: management
    telegram_chat_id: "222222222"
    email: "yossi@example.com"
    categories: [all, monthly_report]
    min_severity: critical
```

Run `solaredge-ops contacts` any time to see exactly who's configured and what
each of them will receive — handy for verifying the directory after editing it:

```
$ solaredge-ops contacts
Danny - Maintenance lead [maintenance] | phone: +972-50-000-0000
    channels: Telegram (chat -1001234567890)
    subscribed to: equipment_offline, zero_production_daylight, low_production, performance_drop, alert_count_jump (minimum severity: warning)
Ronit - Finance [finance]
    channels: Email (ronit@example.com)
    subscribed to: monthly_report (minimum severity: info)
Yossi - CEO [management]
    channels: Telegram (chat 222222222) + Email (yossi@example.com)
    subscribed to: all, monthly_report (minimum severity: critical)
```

## Setup

### 1. Install

```bash
git clone https://github.com/elazarsh/solaredge-ops.git
cd solaredge-ops
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

### 2. Get a SolarEdge API key

In the SolarEdge monitoring portal: **Admin → Site Access → API access** (account-level
keys cover every site on the account; site-level keys are scoped to one site).
Note SolarEdge's published limits: ~300 requests/day per API key *and* per site ID,
and a max of 3 concurrent connections from the same IP. The default polling
interval (30 minutes, active hours only) and the two cheap calls per cycle
(`overview` + `details`) are chosen to comfortably stay under that.

### 3. Create a Telegram bot (optional but recommended)

1. Message [@BotFather](https://t.me/BotFather) on Telegram, send `/newbot`, and
   copy the bot token it gives you.
2. Add the bot to the group chat you want alerts in (e.g. your repair team's group).
3. Get the chat ID — the simplest way is to send a message in the group, then visit
   `https://api.telegram.org/bot<TOKEN>/getUpdates` and read `"chat":{"id": ...}`.

### 4. Configure

```bash
cp config.example.yaml config.yaml
```

Edit `config.yaml`:
- `solaredge.api_key` — the key from step 2
- `sites` — each site's numeric ID (visible in the portal URL or via `solaredge-ops` once running), display name, and an optional `expected_daily_kwh` baseline used by `low_production`
- `polling.active_hours` — the local daylight window worth polling/alerting in
- `alert_rules` — enable/tune the rules you want
- `notifications.telegram` / `notifications.email` — transport settings only (bot token / SMTP server)
- `recipients` — **who** gets **what**: see [Recipients & routing](#recipients--routing) above
- `reporting.monthly` — day of month to generate and send the report on

`config.yaml` is gitignored — it holds secrets and is never committed.

### 5. Try it

```bash
solaredge-ops check --config config.yaml -v     # one alert-check pass, verbose logging
solaredge-ops report --config config.yaml       # send last month's report now
solaredge-ops contacts --config config.yaml     # show who's configured and what they'll receive
solaredge-ops quota --config config.yaml        # see local estimate of remaining API budget
```

### 6. Schedule it

```cron
# Poll every 30 minutes during daylight hours
*/30 6-19 * * *  cd /opt/solaredge-ops && .venv/bin/solaredge-ops check  --config config.yaml >> check.log 2>&1

# Send the monthly report on the 1st
0 6 1 * *        cd /opt/solaredge-ops && .venv/bin/solaredge-ops report --config config.yaml >> report.log 2>&1
```

## Development

```bash
pip install -e ".[dev]"   # or: pip install pytest
pytest
```

The test suite mocks all HTTP (no real SolarEdge/Telegram/SMTP calls) and includes
an end-to-end smoke test (`tests/test_poller_integration.py`) that drives the full
fetch → evaluate → dedup → notify → resolve pipeline against scripted API responses.

## Project layout

```
solaredge_ops/
  api_client.py    SolarEdge REST client + local rate-limit tracking
  config.py        YAML config loading & validation
  models.py        Alert / Severity data model
  rules.py         Pure rule functions: snapshot(s) + config + now -> alerts
  state_store.py   SQLite-backed dedup/state (open alerts, kv state)
  poller.py        Orchestrates one fetch -> evaluate -> dedup -> notify pass
  reporting.py     Monthly production report builder & sender
  notifiers/
    telegram.py    Thin Telegram Bot API transport (send text to a chat ID)
    email.py       Thin SMTP transport (send a message to explicit addresses)
    router.py      AlertRouter: fans alerts out to subscribed `recipients`
  cli.py           `solaredge-ops check|report|contacts|quota`
```
