# Systemd Service Installation Guide

Complete guide for installing InnerOS Automation Daemon as a systemd service.

## Quick Start

### User Mode (Recommended for Single-User Systems)

```bash
# Install daemon service (no root required)
python3 development/scripts/install_daemon.py --user

# Start the daemon
systemctl --user start inneros-daemon

# Enable auto-start on login
systemctl --user enable inneros-daemon

# Check status
systemctl --user status inneros-daemon
```

### System Mode (For Multi-User Servers)

```bash
# Install daemon service (requires root)
sudo python3 development/scripts/install_daemon.py --system --user-name inneros

# Start the daemon
sudo systemctl start inneros-daemon

# Enable auto-start on boot
sudo systemctl enable inneros-daemon

# Check status
sudo systemctl status inneros-daemon
```

## Installation Options

### Interactive Installation
```bash
# Dry run to preview changes
python3 development/scripts/install_daemon.py --user --dry-run

# Full installation with prompts
python3 development/scripts/install_daemon.py --user
```

### Custom Paths
```bash
# Override default paths
python3 development/scripts/install_daemon.py --user \
  --daemon-path /custom/path/inneros-daemon \
  --config-path /custom/path/config.yaml
```

## Service Management

### Starting/Stopping

```bash
# User mode
systemctl --user start inneros-daemon
systemctl --user stop inneros-daemon
systemctl --user restart inneros-daemon

# System mode
sudo systemctl start inneros-daemon
sudo systemctl stop inneros-daemon
sudo systemctl restart inneros-daemon
```

### Viewing Logs

```bash
# User mode - Follow live logs
journalctl --user -u inneros-daemon -f

# System mode - Follow live logs
sudo journalctl -u inneros-daemon -f

# View last 50 lines
journalctl --user -u inneros-daemon -n 50

# View logs since yesterday
journalctl --user -u inneros-daemon --since yesterday
```

### Checking Status

```bash
# User mode
systemctl --user status inneros-daemon

# System mode
sudo systemctl status inneros-daemon
```

## Configuration

### Default Config Locations

- **User mode**: `~/.config/inneros/config.yaml`
- **System mode**: `/etc/inneros/config.yaml`

### Example Configuration

```yaml
daemon:
  check_interval: 60
  log_level: INFO

file_watching:
  enabled: true
  watch_path: ~/knowledge/Inbox
  debounce_seconds: 2.0
  ignore_patterns:
    - "*.tmp"
    - ".git/*"

screenshot_handler:
  enabled: true
  onedrive_path: ~/OneDrive/Screenshots
  knowledge_path: ~/knowledge/Media/Pasted Images
  ocr_enabled: true

smart_link_handler:
  enabled: true
  vault_path: ~/knowledge
  similarity_threshold: 0.75
  max_suggestions: 5
```

## Monitoring

### Health Check

```bash
# Check if daemon is healthy (HTTP endpoint)
curl http://localhost:8080/health

# Expected response:
# {"is_healthy": true, "status_code": 200, ...}
```

### Metrics

```bash
# View Prometheus metrics
curl http://localhost:8080/metrics

# View JSON metrics
curl http://localhost:8080/metrics/json
```

### Terminal Dashboard

```bash
# Live monitoring dashboard
python3 development/demos/terminal_dashboard_live_test.py
```

## Troubleshooting

### Service Won't Start

```bash
# Check service status for errors
systemctl --user status inneros-daemon

# View detailed logs
journalctl --user -u inneros-daemon -n 100

# Verify configuration
python3 -c "from src.automation.config import ConfigurationLoader; \
  print(ConfigurationLoader().load_config(Path('~/.config/inneros/config.yaml').expanduser()))"
```

### Permission Issues

```bash
# User mode - ensure directories exist
mkdir -p ~/.config/inneros ~/.local/share/inneros/logs

# System mode - check user permissions
sudo chown -R inneros:inneros /var/lib/inneros /var/log/inneros
```

### Daemon Not Auto-Starting

```bash
# User mode - enable linger (survives logout)
loginctl enable-linger $USER

# Verify enabled
systemctl --user is-enabled inneros-daemon
```

## Uninstallation

```bash
# User mode
systemctl --user stop inneros-daemon
systemctl --user disable inneros-daemon
rm ~/.config/systemd/user/inneros-daemon.service
systemctl --user daemon-reload

# System mode
sudo systemctl stop inneros-daemon
sudo systemctl disable inneros-daemon
sudo rm /etc/systemd/system/inneros-daemon.service
sudo systemctl daemon-reload
```

## Advanced Configuration

### Custom Service File

Generated service files are located at:
- **User mode**: `~/.config/systemd/user/inneros-daemon.service`
- **System mode**: `/etc/systemd/system/inneros-daemon.service`

After editing, reload systemd:
```bash
systemctl --user daemon-reload  # or sudo systemctl daemon-reload
systemctl --user restart inneros-daemon
```

### Log Rotation

Create `/etc/logrotate.d/inneros-daemon` (system mode):
```
/var/log/inneros/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 inneros inneros
    sharedscripts
    postrotate
        systemctl kill -s HUP inneros-daemon
    endscript
}
```

## Integration with Monitoring Systems

### Prometheus Integration

Add to Prometheus config:
```yaml
scrape_configs:
  - job_name: 'inneros-daemon'
    static_configs:
      - targets: ['localhost:8080']
```

### Grafana Dashboard

Import the dashboard from `development/docs/grafana-dashboard.json` (future enhancement).

## Security Considerations

- **User mode**: Runs with user privileges, safer for single-user systems
- **System mode**: Runs as dedicated user, use for multi-user servers
- **Config permissions**: Ensure config files are not world-readable if they contain sensitive data
- **Network exposure**: HTTP server binds to localhost only by default

---

For more information, see:
- [Feature Handlers Guide](FEATURE-HANDLERS.md)
- [Daemon Architecture](../Projects/ACTIVE/daemon-systemd-service-tdd-iteration-8-lessons-learned.md)
- [Complete Feature Development Workflow](../.windsurf/workflows/complete-feature-development.md)
