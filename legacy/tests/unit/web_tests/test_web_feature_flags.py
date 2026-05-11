"""TDD RED Phase: Web UI feature flag behavior

Phase 6.x P0 - Web UI Feature Flags (GitHub #21)

These tests define expected behavior for Web UI feature flags:
- 7 sensitive routes are gated by centralized feature flags
- When a flag is enabled, existing behavior is preserved (200/500 as before)
- When a flag is disabled, the route fails safely (404 or equivalent)
- Unknown/missing feature flags are treated as disabled (safe default)

All tests should FAIL initially (RED phase) until feature flag system is implemented.
"""

import sys
from pathlib import Path

import pytest


# Add src to path for imports
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent.parent
src_dir = project_root / "development" / "src"
sys.path.insert(0, str(src_dir))

# Import Flask app
web_ui_dir = project_root / "web_ui"
sys.path.insert(0, str(web_ui_dir))

from feature_flags import DEFAULT_FEATURE_FLAGS


@pytest.fixture
def client():
    """Create test Flask client with default feature flag configuration.

    Default behavior: all known features enabled so existing routes continue
    to behave as before. Individual tests can disable specific flags.
    After each test, FEATURE_FLAGS is reset to a safe default so that
    other test modules are not affected by local flag changes.
    """
    from app import app

    app.config["TESTING"] = True

    # Centralized feature flag config expected by app code
    # Keys are logical feature names, not raw URLs
    original_flags = app.config.get("FEATURE_FLAGS")
    app.config["FEATURE_FLAGS"] = DEFAULT_FEATURE_FLAGS.copy()

    with app.test_client() as client:
        try:
            yield client
        finally:
            # Restore previous configuration (or defaults) to avoid
            # leaking disabled flags into other test modules.
            if original_flags is None:
                app.config["FEATURE_FLAGS"] = DEFAULT_FEATURE_FLAGS.copy()
            else:
                app.config["FEATURE_FLAGS"] = original_flags


class TestWebFeatureFlagsEnabledState:
    """Tests for behavior when feature flags are enabled.

    These ensure we do not regress existing happy-path behavior when
    feature flags are ON.
    """

    @pytest.mark.parametrize(
        "route,flag_name",
        [
            ("/dashboard", "dashboard"),
            ("/analytics", "analytics"),
            ("/weekly-review", "weekly_review"),
            ("/api/process-note", "api_process_note"),
            ("/api/metrics", "api_metrics"),
            ("/settings", "settings"),
            ("/onboarding", "onboarding"),
        ],
    )
    def test_routes_accessible_when_feature_enabled(self, client, route, flag_name):
        """When feature flag is True, route should NOT be blocked.

        We intentionally allow 200 or 500 here to avoid coupling to
        existing route-specific safety tests, which already assert more
        detailed behavior. The critical assertion is that the route is
        not gated when the flag is enabled.
        """
        if route == "/api/process-note":
            # /api/process-note only accepts POST, so we exercise the
            # real handler with a minimal valid payload.
            response = client.post(
                route,
                json={
                    "vault_path": "/tmp/vault",
                    "filename": "note.md",
                    "action": "promote",
                },
            )
        else:
            response = client.get(route)

        assert response.status_code in [
            200,
            500,
        ], f"Route {route} should be reachable when feature '{flag_name}' is enabled"


class TestWebFeatureFlagsDisabledState:
    """Tests for behavior when feature flags are disabled.

    These define the new safety behavior introduced by the feature flag
    system: when a flag is OFF, the associated route must fail safely.
    """

    @pytest.mark.parametrize(
        "route,flag_name",
        [
            ("/dashboard", "dashboard"),
            ("/analytics", "analytics"),
            ("/weekly-review", "weekly_review"),
            ("/api/process-note", "api_process_note"),
            ("/api/metrics", "api_metrics"),
            ("/settings", "settings"),
            ("/onboarding", "onboarding"),
        ],
    )
    def test_routes_fail_safely_when_feature_disabled(self, client, route, flag_name):
        """When feature flag is False, route should not behave normally.

        For this iteration we define "fail safely" as returning 404.
        This keeps the implementation simple (Flask abort/404) while
        clearly distinguishing disabled features from normal behavior.
        """
        from app import app

        app.config["FEATURE_FLAGS"][flag_name] = False

        if route == "/api/process-note":
            # /api/process-note only accepts POST, so we exercise the
            # real handler with a minimal valid payload even when
            # checking the disabled behavior.
            response = client.post(
                route,
                json={
                    "vault_path": "/tmp/vault",
                    "filename": "note.md",
                    "action": "promote",
                },
            )
        else:
            response = client.get(route)

        assert (
            response.status_code == 404
        ), f"Route {route} should return 404 when feature '{flag_name}' is disabled"

    def test_unknown_feature_flag_treated_as_disabled(self, client):
        """Unknown or missing feature flag must be treated as disabled.

        This encodes the "safe by default" behavior: if the app asks for a
        feature flag name that is not configured, the corresponding route
        must behave as if the flag were False.
        """
        from app import app

        # Simulate misconfiguration: clear known flags
        app.config["FEATURE_FLAGS"] = {}

        # We expect the implementation to treat missing flags as disabled
        response = client.get("/analytics")

        assert response.status_code == 404, (
            "When FEATURE_FLAGS is missing an entry for 'analytics', the route "
            "should be treated as disabled and return 404"
        )
