# Metrics Export

## Purpose

Export metrics produced by InnerOS for analysis or sharing, using the built-in web endpoint.

## Prereqs

- Web UI running locally (<http://localhost:8081>)
- `.automation/metrics/` is gitignored

## Quick checks

- Verify endpoint is alive:

```bash
curl -s http://localhost:8081/api/metrics | head -n 20
```

- Pretty print with jq (optional):

```bash
curl -s http://localhost:8081/api/metrics | jq '. | {generated_at: .generated_at, latest: .latest}'
```

## Export to dated JSON file

```bash
mkdir -p .automation/metrics/manual
curl -s http://localhost:8081/api/metrics \
  -o ".automation/metrics/manual/metrics_$(date +%Y%m%d_%H%M%S).json"
```

## Minimal CSV (example using jq)

```bash
# Extract a few fields into CSV headers: timestamp,total_notes
curl -s http://localhost:8081/api/metrics \
 | jq -r '[.generated_at, (.latest.metrics.overview.total_notes // 0)] | @csv' \
 >> .automation/metrics/manual/metrics_overview.csv
```

## Schedule (cron)

```bash
# Every hour at minute 5
# (macOS users: cron works; for launchd use a LaunchAgent plist instead)
5 * * * * cd "$HOME/repos/inneros-zettelkasten" && \
  curl -s http://localhost:8081/api/metrics \
    -o ".automation/metrics/manual/metrics_$(date +\%Y\%m\%d_\%H\%M\%S).json"
```

## Pass criteria

- Files appear under `.automation/metrics/` only (and are ignored by git)
- JSON is valid and contains `generated_at`
- Optional CSV accumulates rows over time
