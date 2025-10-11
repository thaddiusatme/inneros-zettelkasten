import logging
from pathlib import Path
from typing import List

from src.automation.daemon import AutomationDaemon
from src.automation.config import (
    DaemonConfig,
    FileWatchConfig,
    ScreenshotHandlerConfig,
    SmartLinkHandlerConfig,
)


class DummyWatcher:
    def __init__(self):
        self._callbacks: List = []

    def register_callback(self, cb):
        self._callbacks.append(cb)

    def is_running(self):
        return True

    @property
    def callbacks(self):
        return list(self._callbacks)


def test_daemon_initializes_handlers_from_config(tmp_path, caplog):
    """Daemon should initialize configured handlers from YAML-derived config."""
    caplog.set_level(logging.INFO)

    screenshots_dir = tmp_path / "OneDrive" / "Pictures" / "Screenshots"
    screenshots_dir.mkdir(parents=True)

    cfg = DaemonConfig(
        file_watching=FileWatchConfig(enabled=False),  # We'll inject a watcher manually
        screenshot_handler=ScreenshotHandlerConfig(
            enabled=True,
            onedrive_path=str(screenshots_dir),
            knowledge_path=str(tmp_path / "knowledge"),
            ocr_enabled=True,
            processing_timeout=600,
        ),
        smart_link_handler=SmartLinkHandlerConfig(
            enabled=True,
            vault_path=str(tmp_path),
            similarity_threshold=0.8,
            max_suggestions=7,
            auto_insert=False,
        ),
    )

    daemon = AutomationDaemon(cfg)
    # Inject a dummy watcher so handler registration works without starting threads
    watcher = DummyWatcher()
    daemon.file_watcher = watcher

    # When: setting up handlers from config
    daemon._setup_feature_handlers()  # No args; should read from config

    # Then: both handlers are initialized with config values
    assert daemon.screenshot_handler is not None
    assert daemon.smart_link_handler is not None

    assert daemon.screenshot_handler.onedrive_path == Path(screenshots_dir)
    assert daemon.smart_link_handler.vault_path == Path(tmp_path)

    # And callbacks were registered
    assert any(getattr(cb, "__name__", "").endswith("process") for cb in watcher.callbacks)


def test_daemon_skips_disabled_handlers(tmp_path):
    """Daemon should skip handlers that are disabled in config."""
    cfg = DaemonConfig(
        file_watching=FileWatchConfig(enabled=False),
        screenshot_handler=ScreenshotHandlerConfig(
            enabled=False,
            onedrive_path=str(tmp_path / "Screenshots"),
        ),
        smart_link_handler=SmartLinkHandlerConfig(
            enabled=False,
            vault_path=str(tmp_path),
        ),
    )

    daemon = AutomationDaemon(cfg)
    daemon.file_watcher = DummyWatcher()

    daemon._setup_feature_handlers()

    assert daemon.screenshot_handler is None
    assert daemon.smart_link_handler is None
    assert len(daemon.file_watcher.callbacks) == 0


def test_daemon_health_includes_handler_metrics(tmp_path):
    screenshots_dir = tmp_path / "OneDrive" / "Pictures" / "Screenshots"
    screenshots_dir.mkdir(parents=True)

    cfg = DaemonConfig(
        file_watching=FileWatchConfig(enabled=False),
        screenshot_handler=ScreenshotHandlerConfig(
            enabled=True,
            onedrive_path=str(screenshots_dir),
        ),
        smart_link_handler=SmartLinkHandlerConfig(
            enabled=True,
            vault_path=str(tmp_path),
        ),
    )

    daemon = AutomationDaemon(cfg)
    daemon.file_watcher = DummyWatcher()
    daemon._setup_feature_handlers()

    health = daemon.get_daemon_health()
    assert 'handlers' in health
    assert 'screenshot' in health['handlers']
    assert 'smart_link' in health['handlers']
    # Screenshot health should include performance keys
    ss = health['handlers']['screenshot']
    assert 'status' in ss


def test_daemon_metrics_export_combines_handler_metrics(tmp_path):
    screenshots_dir = tmp_path / "OneDrive" / "Pictures" / "Screenshots"
    screenshots_dir.mkdir(parents=True)

    cfg = DaemonConfig(
        file_watching=FileWatchConfig(enabled=False),
        screenshot_handler=ScreenshotHandlerConfig(
            enabled=True,
            onedrive_path=str(screenshots_dir),
        ),
        smart_link_handler=SmartLinkHandlerConfig(
            enabled=True,
            vault_path=str(tmp_path),
        ),
    )

    daemon = AutomationDaemon(cfg)
    daemon.file_watcher = DummyWatcher()
    daemon._setup_feature_handlers()

    metrics = daemon.export_handler_metrics()
    assert 'screenshot' in metrics
    assert 'smart_link' in metrics


def test_daemon_exports_prometheus_metrics(tmp_path):
    """Daemon should aggregate Prometheus metrics from all enabled handlers."""
    screenshots_dir = tmp_path / "OneDrive" / "Pictures" / "Screenshots"
    screenshots_dir.mkdir(parents=True)

    cfg = DaemonConfig(
        file_watching=FileWatchConfig(enabled=False),
        screenshot_handler=ScreenshotHandlerConfig(
            enabled=True,
            onedrive_path=str(screenshots_dir),
        ),
        smart_link_handler=SmartLinkHandlerConfig(
            enabled=True,
            vault_path=str(tmp_path),
        ),
    )

    daemon = AutomationDaemon(cfg)
    daemon.file_watcher = DummyWatcher()
    daemon._setup_feature_handlers()

    # When: export Prometheus format
    text = daemon.export_prometheus_metrics()

    # Then: contains standard metric names from handlers
    assert "inneros_handler_processing_seconds" in text
    assert "inneros_handler_events_total" in text
    assert isinstance(text, str)
    assert len(text) > 0
