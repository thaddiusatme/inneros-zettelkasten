#!/usr/bin/env python3
"""
Real Data Validation for LLM Deep Quality Scoring - Issue #90

Compares heuristic vs LLM scoring on actual vault notes.
"""

import sys
import time
import random
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "development"))

from src.ai.enhancer import AIEnhancer
from src.ai.llm_batch_scorer import LLMBatchScorer


def find_sample_notes(vault_path: Path, count: int = 15) -> list:
    """Find a diverse sample of notes from different directories."""
    exclude_dirs = {
        ".git",
        ".obsidian",
        "node_modules",
        ".venv",
        "venv",
        "__pycache__",
        "development",
    }

    all_notes = []
    for md_file in vault_path.rglob("*.md"):
        if not any(excluded in md_file.parts for excluded in exclude_dirs):
            all_notes.append(md_file)

    # Sample from different categories
    categories = {
        "Fleeting Notes": [],
        "Literature Notes": [],
        "Permanent Notes": [],
        "Projects": [],
        "Other": [],
    }

    for note in all_notes:
        categorized = False
        for cat in categories:
            if cat in str(note):
                categories[cat].append(note)
                categorized = True
                break
        if not categorized:
            categories["Other"].append(note)

    # Take samples from each category
    sample = []
    per_category = max(1, count // len(categories))
    for cat, notes in categories.items():
        if notes:
            sample.extend(random.sample(notes, min(per_category, len(notes))))

    # Fill remaining with random notes
    remaining = [n for n in all_notes if n not in sample]
    if len(sample) < count and remaining:
        sample.extend(
            random.sample(remaining, min(count - len(sample), len(remaining)))
        )

    return sample[:count]


def validate_scoring(vault_path: Path, sample_size: int = 15):
    """Run validation comparing heuristic vs LLM scoring."""
    print(f"\n{'='*60}")
    print("LLM Deep Quality Scoring - Real Data Validation")
    print(f"{'='*60}\n")

    # Get sample notes
    print(f"📁 Vault: {vault_path}")
    sample_notes = find_sample_notes(vault_path, sample_size)
    print(f"📝 Sample size: {len(sample_notes)} notes\n")

    enhancer = AIEnhancer()

    # Results storage
    heuristic_results = []
    llm_results = []

    print("=" * 60)
    print("Phase 1: Heuristic Scoring (baseline)")
    print("=" * 60)

    heuristic_start = time.time()
    for i, note_path in enumerate(sample_notes):
        content = note_path.read_text(encoding="utf-8")
        result = enhancer._basic_quality_analysis(content)
        heuristic_results.append(
            {
                "name": note_path.name,
                "score": result["quality_score"],
                "atomic": result.get("zettelkasten_compliance", {}).get("atomic", True),
                "connected": result.get("zettelkasten_compliance", {}).get(
                    "connected", False
                ),
            }
        )
        print(
            f"  [{i+1}/{len(sample_notes)}] {note_path.name[:40]:40} → {result['quality_score']:.2f}"
        )

    heuristic_time = time.time() - heuristic_start
    print(
        f"\n⏱️  Heuristic time: {heuristic_time:.2f}s ({heuristic_time/len(sample_notes)*1000:.1f}ms/note)"
    )

    print("\n" + "=" * 60)
    print("Phase 2: LLM Deep Scoring")
    print("=" * 60)

    llm_start = time.time()
    for i, note_path in enumerate(sample_notes):
        note_start = time.time()
        content = note_path.read_text(encoding="utf-8")
        result = enhancer.analyze_note_quality_deep(content, use_llm=True)
        note_time = time.time() - note_start

        llm_results.append(
            {
                "name": note_path.name,
                "score": result["quality_score"],
                "coherence": result.get("coherence_score", 0),
                "grammar_issues": len(result.get("grammar_issues", [])),
                "mode": result.get("mode", "unknown"),
                "time": note_time,
            }
        )

        mode_icon = "🤖" if result.get("mode") == "llm" else "📊"
        print(
            f"  [{i+1}/{len(sample_notes)}] {note_path.name[:35]:35} → Q:{result['quality_score']:.2f} C:{result.get('coherence_score', 0):.2f} {mode_icon} ({note_time:.1f}s)"
        )

    llm_time = time.time() - llm_start
    print(f"\n⏱️  LLM time: {llm_time:.2f}s ({llm_time/len(sample_notes):.1f}s/note)")

    # Analysis
    print("\n" + "=" * 60)
    print("Analysis: Heuristic vs LLM Comparison")
    print("=" * 60)

    h_scores = [r["score"] for r in heuristic_results]
    l_scores = [r["score"] for r in llm_results]
    l_coherence = [r["coherence"] for r in llm_results]

    print(f"\n📊 Heuristic Scores:")
    print(
        f"   Min: {min(h_scores):.2f}  Max: {max(h_scores):.2f}  Avg: {sum(h_scores)/len(h_scores):.2f}"
    )

    print(f"\n🤖 LLM Quality Scores:")
    print(
        f"   Min: {min(l_scores):.2f}  Max: {max(l_scores):.2f}  Avg: {sum(l_scores)/len(l_scores):.2f}"
    )

    print(f"\n🧠 LLM Coherence Scores:")
    print(
        f"   Min: {min(l_coherence):.2f}  Max: {max(l_coherence):.2f}  Avg: {sum(l_coherence)/len(l_coherence):.2f}"
    )

    # Score correlation
    diffs = [abs(h - l) for h, l in zip(h_scores, l_scores)]
    print(f"\n📈 Score Difference (Heuristic vs LLM):")
    print(f"   Avg diff: {sum(diffs)/len(diffs):.2f}  Max diff: {max(diffs):.2f}")

    # Performance comparison
    print(f"\n⚡ Performance:")
    print(f"   Heuristic: {heuristic_time/len(sample_notes)*1000:.1f}ms/note")
    print(f"   LLM:       {llm_time/len(sample_notes):.1f}s/note")
    print(f"   Ratio:     {llm_time/heuristic_time:.0f}x slower")

    # LLM mode success rate
    llm_mode_count = sum(1 for r in llm_results if r["mode"] == "llm")
    print(
        f"\n🎯 LLM Success Rate: {llm_mode_count}/{len(llm_results)} ({100*llm_mode_count/len(llm_results):.0f}%)"
    )

    # ETA for full vault
    total_notes = len(list(vault_path.rglob("*.md")))
    llm_eta_seconds = total_notes * (llm_time / len(sample_notes))
    llm_eta_hours = llm_eta_seconds / 3600
    print(f"\n📅 Full Vault ETA ({total_notes} notes):")
    print(f"   Heuristic: {total_notes * heuristic_time / len(sample_notes):.1f}s")
    print(f"   LLM:       {llm_eta_hours:.1f}h ({llm_eta_seconds/60:.0f}m)")

    print("\n" + "=" * 60)
    print("✅ Validation Complete")
    print("=" * 60 + "\n")

    return {
        "sample_size": len(sample_notes),
        "heuristic_avg": sum(h_scores) / len(h_scores),
        "llm_avg": sum(l_scores) / len(l_scores),
        "coherence_avg": sum(l_coherence) / len(l_coherence),
        "llm_success_rate": llm_mode_count / len(llm_results),
        "llm_time_per_note": llm_time / len(sample_notes),
        "full_vault_eta_hours": llm_eta_hours,
    }


if __name__ == "__main__":
    vault = project_root
    results = validate_scoring(vault, sample_size=10)
