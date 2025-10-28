import json
from pathlib import Path

import pytest

from src.perplexity_fetcher import fetch_from_jsonl, slugify


def test_slugify_basic():
    assert (
        slugify("One spoon equals instant Moroccan dinner")
        == "one-spoon-equals-instant-moroccan-dinner"
    )
    assert (
        slugify("Cooking vs finishing oils in Moroccan cuisine")
        == "cooking-vs-finishing-oils-in-moroccan-cuisine"
    )


def test_fetch_from_jsonl_dry_run_creates_outputs(tmp_path: Path):
    # Arrange: create a minimal JSONL input with two items
    items = [
        {
            "title": "One spoon equals instant Moroccan dinner",
            "tags": ["mustapha-social-campaign"],
            "prompt": 'Title: "One spoon equals instant Moroccan dinner"\nObjective: ...',
        },
        {
            "title": "Cooking vs finishing oils in Moroccan cuisine",
            "tags": ["mustapha-social-campaign"],
            "prompt": 'Title: "Cooking vs finishing oils in Moroccan cuisine"\nObjective: ...',
        },
    ]
    jsonl_path = tmp_path / "briefs.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as f:
        for obj in items:
            f.write(json.dumps(obj) + "\n")

    out_dir = tmp_path / "out"

    # Act: dry run (no API calls) should still create structured outputs
    results = fetch_from_jsonl(
        input_path=str(jsonl_path),
        output_dir=str(out_dir),
        model="sonar-pro",
        dry_run=True,
    )

    # Assert: two outputs created with expected filenames and scaffold content
    assert len(results) == 2
    expected_files = {
        out_dir / "perplexity-output-one-spoon-equals-instant-moroccan-dinner.md",
        out_dir / "perplexity-output-cooking-vs-finishing-oils-in-moroccan-cuisine.md",
    }
    assert set(Path(p) for p in results) == expected_files

    for p in expected_files:
        content = p.read_text(encoding="utf-8")
        assert "# Executive Summary" in content
        assert "# Core Claims" in content
        assert "# Sources" in content
        # Dry-run should also include the original prompt as reference
        assert "Original Prompt" in content


@pytest.mark.skip(
    reason="Network call; enable when PERPLEXITY_API_KEY is configured and network calls are allowed"
)
def test_fetch_real_api_call(tmp_path: Path):
    # This test is opt-in and will perform a real API call when enabled.
    item = {
        "title": "Preserved lemons, the magic ingredient you are sleeping on",
        "tags": ["mustapha-social-campaign"],
        "prompt": 'Title: "Preserved lemons, the magic ingredient you are sleeping on"\nObjective: ...',
    }
    jsonl_path = tmp_path / "briefs.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as f:
        f.write(json.dumps(item) + "\n")

    out_dir = tmp_path / "out"
    results = fetch_from_jsonl(
        input_path=str(jsonl_path),
        output_dir=str(out_dir),
        model="sonar-pro",
        dry_run=False,
    )

    assert len(results) == 1
    p = Path(results[0])
    assert p.exists()
    content = p.read_text(encoding="utf-8")
    # Basic sanity check for some non-empty output
    assert len(content) > 50
