# InnerOS Dashboard Commands

Quick access to system monitoring and workflow dashboards.

## Commands

### Web Dashboard (Interactive UI)

Launch the interactive workflow dashboard with status panels and quick actions:

```bash
inneros dashboard
```

Features:
- Inbox status with quality scores
- Fleeting note health monitoring
- Weekly review candidates
- Quick action menu
- Real-time status updates

**Options:**
```bash
inneros dashboard /path/to/vault  # Custom vault location
```

The dashboard will:
- Launch in background (non-blocking)
- Display URL (typically http://localhost:8000)
- Stay running until you press Ctrl+C

### Live Terminal Mode

Launch the live terminal dashboard for real-time daemon monitoring:

```bash
inneros dashboard --live
```

Features:
- Real-time daemon health status
- Handler processing metrics
- Live-updating display
- Color-coded indicators (🟢 healthy, 🔴 unhealthy)

**Options:**
```bash
inneros dashboard --live --daemon-url http://localhost:9999
```

The terminal dashboard will:
- Block and show live metrics
- Update every second
- Exit when you press Ctrl+C

## Use Cases

### Quick System Check
```bash
# Launch web dashboard to see overall status
inneros dashboard
```

### Monitor Daemon Activity
```bash
# Watch daemon processing in real-time
inneros dashboard --live
```

### Custom Configuration
```bash
# Monitor daemon on custom port
inneros dashboard --live --daemon-url http://localhost:8080
```

## Process Management

### Duplicate Prevention
The dashboard launcher automatically detects if a dashboard is already running:

```bash
$ inneros dashboard
❌ Dashboard already running
   URL: http://localhost:8000
```

### Stopping Dashboards

**Web Dashboard:**
- Press `Ctrl+C` in the terminal where you launched it
- Or kill the process manually

**Live Terminal Dashboard:**
- Press `Ctrl+C` to exit gracefully

## Error Handling

### Common Errors

**Port Conflict:**
```bash
❌ Dashboard process exited immediately (possible port conflict)
```
**Solution**: Stop the conflicting process or use a different port.

**Dashboard Not Found:**
```bash
❌ Dashboard script not found: /path/to/workflow_dashboard.py
```
**Solution**: Ensure you're running from the correct directory.

**Permission Denied:**
```bash
❌ Permission denied: ...
```
**Solution**: Check file permissions or run with appropriate privileges.

## Integration with Other Commands

### Combined with Status
```bash
# Check system status first
inneros status

# Then launch dashboard for detailed view
inneros dashboard
```

### Combined with Daemon
```bash
# Start daemon
inneros daemon start

# Monitor with live dashboard
inneros dashboard --live
```

## Architecture

### Files
- `dashboard_cli.py` - Main CLI entry point
- `dashboard_utils.py` - Launcher utilities
- `workflow_dashboard.py` - Web UI implementation
- `terminal_dashboard.py` - Live terminal implementation

### Pattern
The dashboard launcher uses a **facade pattern**:
- Lightweight CLI wrapper (185 LOC)
- Delegates to full-featured dashboards
- Clean separation of concerns

## Development

### Testing
```bash
# Run verification scripts
cd development
python3 tests/verify_refactor_phase.py
```

### Adding New Dashboard Types
1. Create dashboard implementation (e.g., `new_dashboard.py`)
2. Add launcher utility to `dashboard_utils.py`
3. Add facade class to `dashboard_cli.py`
4. Add CLI arguments to `main()`

## Troubleshooting

### Dashboard Doesn't Start
1. Check if port 8000 is available
2. Verify vault path exists
3. Check Python environment

### Live Dashboard No Data
1. Confirm daemon is running: `inneros status`
2. Check daemon URL is correct
3. Verify daemon HTTP server is enabled

### Process Won't Stop
1. Use `Ctrl+C` first
2. Find process: `ps aux | grep dashboard`
3. Kill manually: `kill <pid>`

## See Also

- `inneros status` - System status overview
- `inneros daemon` - Daemon management commands
- System Observability Integration Manifest (Projects/ACTIVE/)

---

**Version**: 2.3.0-dashboard-launcher  
**Date**: 2025-10-15  
**Status**: Production Ready
