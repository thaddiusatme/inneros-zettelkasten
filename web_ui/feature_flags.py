"""Web UI feature flag utilities for InnerOS Zettelkasten.

Centralized configuration and helpers for gating sensitive web routes.

Design goals:
- All feature flags live in one place (DEFAULT_FEATURE_FLAGS)
- Flask app config can override defaults via app.config["FEATURE_FLAGS"]
- Unknown/missing flags are treated as disabled (safe by default)
- Reusable decorator require_feature("name") keeps route code clean
"""

from functools import wraps
from typing import Dict

from flask import abort, current_app


# Centralized default configuration for web UI feature flags.
#
# These defaults are used when the Flask app does not provide an explicit
# FEATURE_FLAGS mapping. Tests and environments can override the mapping by
# setting app.config["FEATURE_FLAGS"].
DEFAULT_FEATURE_FLAGS: Dict[str, bool] = {
    "dashboard": True,
    "analytics": True,
    "weekly_review": True,
    "api_process_note": True,
    "api_metrics": True,
    "settings": True,
    "onboarding": True,
}


def get_feature_flags(app) -> Dict[str, bool]:
    """Return the feature flag mapping for the given Flask app.

    If FEATURE_FLAGS is not configured, fall back to DEFAULT_FEATURE_FLAGS
    and attach a copy to app.config so subsequent lookups are consistent.
    """
    flags = app.config.get("FEATURE_FLAGS")
    if flags is None:
        flags = DEFAULT_FEATURE_FLAGS.copy()
        app.config["FEATURE_FLAGS"] = flags
    return flags


def is_feature_enabled(app, flag_name: str) -> bool:
    """Check whether a feature is enabled for the given app.

    Unknown or missing feature names are treated as disabled (safe by
    default) by returning False.
    """
    flags = get_feature_flags(app)
    return bool(flags.get(flag_name, False))


def require_feature(flag_name: str):
    """Decorator to gate a Flask route behind a feature flag.

    When the specified feature is disabled or missing, the route returns
    a 404 response via flask.abort(404). When enabled, the wrapped view
    function executes normally.
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            app = current_app
            if not is_feature_enabled(app, flag_name):
                # Fail safely when feature is disabled or misconfigured
                abort(404)
            return view_func(*args, **kwargs)

        return wrapped

    return decorator
