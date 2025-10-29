"""
InnerOS Zettelkasten Web UI - Flask Application
AI-enhanced knowledge management dashboard
"""

import sys
import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
from datetime import datetime

# Add the src directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_dir = os.path.join(project_root, "development", "src")
sys.path.insert(0, src_dir)

# Import AI modules
from src.ai.analytics import NoteAnalytics
from src.ai.workflow_manager import WorkflowManager
from src.cli.weekly_review_formatter import WeeklyReviewFormatter

# Import monitoring modules
from src.monitoring.metrics_collector import MetricsCollector
from src.monitoring.metrics_storage import MetricsStorage
from src.monitoring.metrics_endpoint import MetricsEndpoint

# Import web metrics utilities
from web_metrics_utils import (
    WebMetricsFormatter,
    MetricsCoordinatorIntegration,
    WebMetricsErrorHandler,
)

app = Flask(__name__)
app.secret_key = "inneros-zettelkasten-demo-key"  # Change in production

# Global configuration
DEFAULT_VAULT_PATH = os.path.expanduser("~/repos/inneros-zettelkasten/knowledge")

# Initialize metrics infrastructure
metrics_collector = MetricsCollector()
metrics_storage = MetricsStorage()
metrics_endpoint = MetricsEndpoint(metrics_collector, metrics_storage)

# Initialize web metrics utilities
metrics_formatter = WebMetricsFormatter(enable_cors=True)
metrics_coordinator = MetricsCoordinatorIntegration(metrics_endpoint)
metrics_error_handler = WebMetricsErrorHandler()


@app.route("/")
def index():
    """Home page with overview of InnerOS Zettelkasten."""
    return render_template(
        "index.html",
        title="InnerOS Zettelkasten",
        current_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )


@app.route("/dashboard")
def dashboard():
    """System dashboard with real-time metrics visualization.

    STUB for TDD RED phase - will be implemented in GREEN phase.
    """
    return render_template(
        "dashboard.html",
        title="Dashboard",
        current_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )


@app.route("/analytics")
def analytics():
    """Analytics dashboard showing note collection insights."""
    vault_path = request.args.get("path", DEFAULT_VAULT_PATH)

    try:
        analytics = NoteAnalytics(vault_path)
        stats = analytics.generate_report()

        # Type guard: Ensure stats is a dictionary
        if not isinstance(stats, dict):
            raise TypeError(
                f"Expected dict from generate_report(), got {type(stats).__name__}: {stats}"
            )

        # Prepare data for web display (handle actual analytics structure)
        overview = stats.get("overview", {})
        quality_metrics = stats.get("quality_metrics", {})

        dashboard_data = {
            "total_notes": overview.get("total_notes", 0),
            "quality_distribution": {
                "high": quality_metrics.get("high_quality_notes", 0),
                "medium": quality_metrics.get("medium_quality_notes", 0),
                "low": quality_metrics.get("low_quality_notes", 0),
            },
            "ai_adoption": {
                "tagged_notes": 0,  # Will be enhanced later
                "enhanced_notes": 0,
                "summarized_notes": overview.get("notes_with_ai_summaries", 0),
                "connected_notes": 0,
            },
            "recent_notes": [],  # Will be enhanced when note details are available
            "recommendations": stats.get("recommendations", []),
            "vault_path": vault_path,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        return render_template(
            "analytics.html", data=dashboard_data, title="Analytics Dashboard"
        )

    except Exception as e:
        error_message = f"Error loading analytics: {str(e)}"
        return render_template(
            "error.html", error=error_message, title="Analytics Error"
        )


@app.route("/weekly-review")
def weekly_review():
    """Weekly review interface with AI recommendations."""
    vault_path = request.args.get("path", DEFAULT_VAULT_PATH)

    try:
        # Quick scan without full AI processing to avoid timeout
        from pathlib import Path

        vault = Path(vault_path)
        inbox_notes = (
            list(vault.glob("Inbox/*.md")) if (vault / "Inbox").exists() else []
        )
        fleeting_notes = (
            list(vault.glob("Fleeting Notes/*.md"))
            if (vault / "Fleeting Notes").exists()
            else []
        )

        # Simple review data without expensive AI processing
        # Convert notes to simple recommendation format for template
        inbox_items = [
            {
                "filename": n.name,
                "title": n.stem,
                "reason": "In inbox",
                "quality_score": 0.5,  # Default placeholder
                "confidence": 0.7,  # Default placeholder
            }
            for n in inbox_notes[:20]
        ]
        fleeting_items = [
            {
                "filename": n.name,
                "title": n.stem,
                "reason": "Fleeting note",
                "quality_score": 0.4,  # Default placeholder
                "confidence": 0.6,  # Default placeholder
            }
            for n in fleeting_notes[:20]
        ]

        review_data = {
            "candidates_count": len(inbox_notes) + len(fleeting_notes),
            "recommendations": {
                "promote": inbox_items[
                    :10
                ],  # Show first 10 inbox notes as promotion candidates
                "keep": fleeting_items[:10],  # Show first 10 fleeting notes
                "improve": [],  # Empty for now
            },
            "vault_path": vault_path,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        return render_template(
            "weekly_review.html", data=review_data, title="Weekly Review"
        )

    except Exception as e:
        import traceback

        print(f"ERROR in weekly-review: {str(e)}")
        traceback.print_exc()
        error_message = f"Error loading weekly review: {str(e)}"
        return render_template(
            "error.html", error=error_message, title="Weekly Review Error"
        )


@app.route("/api/process-note", methods=["POST"])
def process_note():
    """API endpoint to process a single note from weekly review."""
    data = request.get_json()
    vault_path = data.get("vault_path", DEFAULT_VAULT_PATH)
    filename = data.get("filename")
    action = data.get("action")  # 'promote', 'keep', 'improve'

    try:
        workflow_manager = WorkflowManager(vault_path)
        # This would implement actual note processing logic
        result = {
            "success": True,
            "message": f"Successfully {action}d {filename}",
            "filename": filename,
            "action": action,
        }
        return jsonify(result)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/metrics")
def api_metrics():
    """API endpoint for real-time metrics data.

    Returns JSON with current metrics and history for dashboard display.
    Uses WebMetricsFormatter for response formatting and error handling.
    """
    try:
        # Get combined metrics from endpoint and coordinator
        metrics_data = metrics_coordinator.get_combined_metrics()

        # Format response with CORS headers
        return metrics_formatter.format_metrics_response(metrics_data)

    except Exception as e:
        # Log error and return graceful fallback
        metrics_error_handler.handle_metrics_error(e, "api_metrics")
        fallback_data = metrics_formatter.format_fallback_response(e)
        return metrics_formatter.format_metrics_response(fallback_data)


@app.route("/settings")
def settings():
    """Settings page for vault configuration."""
    return render_template(
        "settings.html", title="Settings", current_vault=DEFAULT_VAULT_PATH
    )


@app.route("/onboarding")
def onboarding():
    """Onboarding flow for new users."""
    return render_template("onboarding.html", title="Welcome to InnerOS Zettelkasten")


def _calculate_quality_distribution(stats):
    """Calculate quality score distribution for dashboard."""
    notes = stats.get("notes", [])
    if not notes:
        return {"high": 0, "medium": 0, "low": 0}

    high = sum(1 for note in notes if note.get("quality_score", 0) >= 0.7)
    medium = sum(1 for note in notes if 0.4 <= note.get("quality_score", 0) < 0.7)
    low = sum(1 for note in notes if note.get("quality_score", 0) < 0.4)

    return {"high": high, "medium": medium, "low": low}


if __name__ == "__main__":
    print("🚀 Starting InnerOS Zettelkasten Web UI...")
    print(f"📁 Default vault: {DEFAULT_VAULT_PATH}")
    print("🌐 Access at: http://localhost:8081")

    app.run(debug=True, host="0.0.0.0", port=8081)
