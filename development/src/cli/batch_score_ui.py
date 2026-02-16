#!/usr/bin/env python3
"""
Batch Quality Scoring with Live Web UI

Scores all notes in the vault and provides real-time progress via web interface.
"""

import sys
from pathlib import Path
from flask import Flask, render_template_string, Response, jsonify, request
import json
import time
from threading import Thread
import queue

# Add src to path
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent
sys.path.insert(0, str(project_root / "development"))

from src.ai.enhancer import AIEnhancer

app = Flask(__name__)

# Global state for progress tracking
scoring_state = {
    "status": "idle",  # idle, running, complete, error
    "total": 0,
    "processed": 0,
    "current_file": "",
    "results": [],
    "start_time": None,
    "errors": [],
    "mode": "heuristic",  # heuristic or llm
}

# Queue for SSE updates
update_queue = queue.Queue()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>InnerOS Batch Quality Scoring</title>
    <style>
        * { box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px;
            background: #1a1a2e;
            color: #eee;
        }
        h1 { color: #00d4ff; }
        .controls { 
            background: #16213e; 
            padding: 20px; 
            border-radius: 8px; 
            margin-bottom: 20px;
        }
        input[type="text"] {
            width: 100%;
            padding: 12px;
            font-size: 16px;
            border: 1px solid #0f3460;
            border-radius: 4px;
            background: #0f3460;
            color: #eee;
            margin-bottom: 10px;
        }
        button {
            background: #00d4ff;
            color: #1a1a2e;
            border: none;
            padding: 12px 24px;
            font-size: 16px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
        }
        button:hover { background: #00b8e6; }
        button:disabled { background: #555; cursor: not-allowed; }
        .progress-container {
            background: #16213e;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .progress-bar {
            width: 100%;
            height: 30px;
            background: #0f3460;
            border-radius: 4px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00d4ff, #00ff88);
            transition: width 0.3s;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-top: 15px;
        }
        .stat {
            background: #0f3460;
            padding: 15px;
            border-radius: 4px;
            text-align: center;
        }
        .stat-value { font-size: 24px; font-weight: bold; color: #00d4ff; }
        .stat-label { font-size: 12px; color: #888; margin-top: 5px; }
        .current-file {
            background: #0f3460;
            padding: 10px 15px;
            border-radius: 4px;
            margin-top: 15px;
            font-family: monospace;
            font-size: 14px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .results {
            background: #16213e;
            padding: 20px;
            border-radius: 8px;
        }
        .results h2 { margin-top: 0; color: #00d4ff; }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #0f3460;
        }
        th { color: #00d4ff; }
        .score-high { color: #00ff88; }
        .score-medium { color: #ffcc00; }
        .score-low { color: #ff4444; }
        .status-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }
        .status-idle { background: #555; }
        .status-running { background: #00d4ff; color: #1a1a2e; }
        .status-complete { background: #00ff88; color: #1a1a2e; }
        .status-error { background: #ff4444; }
    </style>
</head>
<body>
    <h1>🎯 InnerOS Batch Quality Scoring</h1>
    
    <div class="controls">
        <input type="text" id="vaultPath" placeholder="Vault path (e.g., /Users/you/vault)" 
               value="{{ default_path }}">
        <button id="startBtn" onclick="startScoring()">▶️ Start Scoring</button>
        <span id="statusBadge" class="status-badge status-idle">IDLE</span>
    </div>
    
    <div class="progress-container">
        <div class="progress-bar">
            <div class="progress-fill" id="progressFill" style="width: 0%"></div>
        </div>
        <div class="stats">
            <div class="stat">
                <div class="stat-value" id="processed">0</div>
                <div class="stat-label">Processed</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="total">0</div>
                <div class="stat-label">Total</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="avgScore">-</div>
                <div class="stat-label">Avg Score</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="eta">-</div>
                <div class="stat-label">ETA</div>
            </div>
        </div>
        <div class="current-file" id="currentFile">Ready to start...</div>
    </div>
    
    <div class="results">
        <h2>📊 Results</h2>
        <table>
            <thead>
                <tr>
                    <th>Note</th>
                    <th>Score</th>
                    <th>Placeholders</th>
                    <th>Atomic</th>
                    <th>Connected</th>
                </tr>
            </thead>
            <tbody id="resultsTable">
                <tr><td colspan="5" style="text-align: center; color: #666;">No results yet</td></tr>
            </tbody>
        </table>
    </div>

    <script>
        let eventSource = null;
        
        function startScoring() {
            const path = document.getElementById('vaultPath').value;
            if (!path) {
                alert('Please enter a vault path');
                return;
            }
            
            document.getElementById('startBtn').disabled = true;
            document.getElementById('resultsTable').innerHTML = '';
            
            // Start SSE connection
            if (eventSource) eventSource.close();
            eventSource = new EventSource('/stream');
            
            eventSource.onmessage = function(e) {
                const data = JSON.parse(e.data);
                updateUI(data);
            };
            
            eventSource.onerror = function() {
                document.getElementById('startBtn').disabled = false;
            };
            
            // Start scoring
            fetch('/start', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({path: path})
            });
        }
        
        function updateUI(data) {
            // Status badge
            const badge = document.getElementById('statusBadge');
            badge.textContent = data.status.toUpperCase();
            badge.className = 'status-badge status-' + data.status;
            
            // Progress
            const pct = data.total > 0 ? (data.processed / data.total * 100) : 0;
            document.getElementById('progressFill').style.width = pct + '%';
            document.getElementById('processed').textContent = data.processed;
            document.getElementById('total').textContent = data.total;
            
            // Current file
            document.getElementById('currentFile').textContent = 
                data.current_file || (data.status === 'complete' ? '✅ Complete!' : 'Ready...');
            
            // Average score
            if (data.results && data.results.length > 0) {
                const avg = data.results.reduce((a, b) => a + b.score, 0) / data.results.length;
                document.getElementById('avgScore').textContent = (avg * 100).toFixed(0) + '%';
            }
            
            // ETA
            if (data.eta) {
                document.getElementById('eta').textContent = data.eta;
            }
            
            // Results table
            if (data.latest_result) {
                const r = data.latest_result;
                const scoreClass = r.score >= 0.7 ? 'score-high' : (r.score >= 0.4 ? 'score-medium' : 'score-low');
                const row = `<tr>
                    <td>${r.name}</td>
                    <td class="${scoreClass}">${(r.score * 100).toFixed(0)}%</td>
                    <td>${r.has_placeholders ? '⚠️ Yes' : '✅ No'}</td>
                    <td>${r.atomic ? '✅' : '❌'}</td>
                    <td>${r.connected ? '✅' : '❌'}</td>
                </tr>`;
                document.getElementById('resultsTable').insertAdjacentHTML('afterbegin', row);
            }
            
            // Re-enable button when done
            if (data.status === 'complete' || data.status === 'error') {
                document.getElementById('startBtn').disabled = false;
                if (eventSource) eventSource.close();
            }
        }
    </script>
</body>
</html>
"""


def find_all_notes(vault_path: Path) -> list:
    """Find all markdown notes in the vault."""
    notes = []
    exclude_dirs = {".git", ".obsidian", "node_modules", ".venv", "venv", "__pycache__"}

    for md_file in vault_path.rglob("*.md"):
        # Skip excluded directories
        if any(excluded in md_file.parts for excluded in exclude_dirs):
            continue
        notes.append(md_file)

    return notes


def score_notes_worker(vault_path: str, use_llm: bool = False, resume: bool = False):
    """Worker thread that scores notes and updates state."""
    global scoring_state

    try:
        vault = Path(vault_path)
        if not vault.exists():
            scoring_state["status"] = "error"
            scoring_state["errors"].append(f"Path not found: {vault_path}")
            update_queue.put(dict(scoring_state))
            return

        notes = find_all_notes(vault)
        scoring_state["total"] = len(notes)
        scoring_state["status"] = "running"
        scoring_state["start_time"] = time.time()
        scoring_state["results"] = []
        scoring_state["errors"] = []
        scoring_state["mode"] = "llm" if use_llm else "heuristic"

        # Load checkpoint if resuming
        checkpoint_path = vault / ".llm_scoring_checkpoint.json"
        scored_notes = {}
        if resume and checkpoint_path.exists():
            try:
                checkpoint = json.loads(checkpoint_path.read_text())
                scored_notes = checkpoint.get("scored_notes", {})
            except (json.JSONDecodeError, IOError):
                pass

        update_queue.put(dict(scoring_state))

        enhancer = AIEnhancer()

        for i, note_path in enumerate(notes):
            # Skip already scored notes if resuming
            if note_path.name in scored_notes:
                note_result = scored_notes[note_path.name]
                scoring_state["results"].append(note_result)
                scoring_state["processed"] = i + 1
                scoring_state["current_file"] = note_path.name
                continue

            try:
                content = note_path.read_text(encoding="utf-8")

                if use_llm:
                    result = enhancer.analyze_note_quality_deep(content, use_llm=True)
                    # Compute content-based fields via heuristic analysis (fix #91)
                    heuristic = enhancer._basic_quality_analysis(content)
                    note_result = {
                        "name": note_path.name,
                        "path": str(note_path),
                        "score": result["quality_score"],
                        "coherence_score": result.get("coherence_score", 0),
                        "grammar_issues": result.get("grammar_issues", []),
                        "zettelkasten_feedback": result.get(
                            "zettelkasten_feedback", {}
                        ),
                        "has_placeholders": heuristic.get("has_placeholders", False),
                        "atomic": heuristic.get("zettelkasten_compliance", {}).get(
                            "atomic", True
                        ),
                        "connected": heuristic.get("zettelkasten_compliance", {}).get(
                            "connected", False
                        ),
                    }
                else:
                    result = enhancer._basic_quality_analysis(content)
                    note_result = {
                        "name": note_path.name,
                        "path": str(note_path),
                        "score": result["quality_score"],
                        "has_placeholders": result.get("has_placeholders", False),
                        "atomic": result.get("zettelkasten_compliance", {}).get(
                            "atomic", True
                        ),
                        "connected": result.get("zettelkasten_compliance", {}).get(
                            "connected", False
                        ),
                        "breakdown": result.get("score_breakdown", {}),
                    }

                scoring_state["results"].append(note_result)
                scored_notes[note_path.name] = note_result

                # Save checkpoint for LLM mode
                if use_llm:
                    checkpoint_path.write_text(
                        json.dumps(
                            {
                                "scored_notes": scored_notes,
                                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                            },
                            indent=2,
                        )
                    )

            except Exception as e:
                scoring_state["errors"].append(f"{note_path.name}: {str(e)}")
                note_result = {"name": note_path.name, "score": 0, "error": str(e)}

            scoring_state["processed"] = i + 1
            scoring_state["current_file"] = note_path.name

            # Calculate ETA
            elapsed = time.time() - scoring_state["start_time"]
            if i > 0:
                rate = elapsed / (i + 1)
                remaining = (len(notes) - i - 1) * rate
                scoring_state["eta"] = f"{int(remaining)}s"

            # Send update
            state_copy = dict(scoring_state)
            state_copy["latest_result"] = note_result
            update_queue.put(state_copy)

        scoring_state["status"] = "complete"
        scoring_state["current_file"] = ""
        update_queue.put(dict(scoring_state))

    except Exception as e:
        scoring_state["status"] = "error"
        scoring_state["errors"].append(str(e))
        update_queue.put(dict(scoring_state))


@app.route("/")
def index():
    default_path = str(project_root)
    return render_template_string(HTML_TEMPLATE, default_path=default_path)


@app.route("/start", methods=["POST"])
def start_scoring():
    global scoring_state

    data = request.json
    vault_path = data.get("path", "")
    use_llm = data.get("use_llm", False)
    resume = data.get("resume", False)

    # Reset state
    scoring_state = {
        "status": "idle",
        "total": 0,
        "processed": 0,
        "current_file": "",
        "results": [],
        "start_time": None,
        "errors": [],
        "mode": "llm" if use_llm else "heuristic",
    }

    # Start worker thread
    thread = Thread(target=score_notes_worker, args=(vault_path, use_llm, resume))
    thread.daemon = True
    thread.start()

    return jsonify({"status": "started"})


@app.route("/stream")
def stream():
    def generate():
        while True:
            try:
                data = update_queue.get(timeout=30)
                yield f"data: {json.dumps(data)}\n\n"
                if data.get("status") in ("complete", "error"):
                    break
            except queue.Empty:
                # Send heartbeat
                yield f"data: {json.dumps(scoring_state)}\n\n"

    return Response(generate(), mimetype="text/event-stream")


@app.route("/estimate")
def estimate_time():
    """Estimate completion time for batch scoring."""
    vault_path = request.args.get("path", "")
    use_llm = request.args.get("use_llm", "false").lower() == "true"

    if not vault_path:
        return jsonify({"error": "path parameter required"}), 400

    vault = Path(vault_path)
    if not vault.exists():
        return jsonify({"error": f"Path not found: {vault_path}"}), 404

    notes = find_all_notes(vault)
    total_notes = len(notes)

    if use_llm:
        # LLM mode: ~3 seconds per note average
        seconds_per_note = 3.0
    else:
        # Heuristic mode: ~0.001 seconds per note
        seconds_per_note = 0.001

    estimated_seconds = total_notes * seconds_per_note

    # Format human-readable time
    if estimated_seconds < 60:
        estimated_time = f"{int(estimated_seconds)}s"
    elif estimated_seconds < 3600:
        minutes = int(estimated_seconds / 60)
        seconds = int(estimated_seconds % 60)
        estimated_time = f"{minutes}m {seconds}s"
    else:
        hours = int(estimated_seconds / 3600)
        minutes = int((estimated_seconds % 3600) / 60)
        estimated_time = f"{hours}h {minutes}m"

    return jsonify(
        {
            "total_notes": total_notes,
            "estimated_seconds": estimated_seconds,
            "estimated_time": estimated_time,
            "mode": "llm" if use_llm else "heuristic",
        }
    )


@app.route("/results")
def get_results():
    return jsonify(scoring_state)


if __name__ == "__main__":
    print("🎯 Starting Batch Quality Scoring UI...")
    print("🌐 Open: http://localhost:8082")
    print("📁 Default vault:", project_root)
    app.run(debug=False, host="0.0.0.0", port=8082, threaded=True)
