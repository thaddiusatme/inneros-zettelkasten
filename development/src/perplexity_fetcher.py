import json
import os
import re
from pathlib import Path
from typing import Iterable, List, Dict, Any, Optional

import datetime

try:
    import requests  # optional for real API calls
except Exception:  # pragma: no cover
    requests = None  # type: ignore


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text


def _read_jsonl(path: str) -> Iterable[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _markdown_scaffold(
    title: str, prompt: str, body: Optional[str] = None, include_prompt: bool = True
) -> str:
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    parts: List[str] = []
    parts.append(f"# Perplexity Research — {title}")
    parts.append("")
    parts.append(f"Generated: {ts}")
    parts.append("")
    if body:
        parts.append(body)
        parts.append("")
    parts.append("# Executive Summary")
    parts.append("")
    parts.append("# Core Claims")
    parts.append("")
    parts.append("# Practical Guidance")
    parts.append("")
    parts.append("# Myths vs Reality")
    parts.append("")
    parts.append("# Risk and Counterpoints")
    parts.append("")
    parts.append("# Sources")
    parts.append("")
    if include_prompt:
        parts.append("---")
        parts.append("")
        parts.append("## Original Prompt")
        parts.append("")
        parts.append("```text")
        parts.append(prompt)
        parts.append("```")
    return "\n".join(parts)


def _call_perplexity_api(
    prompt: str, model: str = "sonar-pro", api_key: Optional[str] = None
) -> str:
    api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise RuntimeError("PERPLEXITY_API_KEY not set; cannot perform real API call")
    if requests is None:
        raise RuntimeError("requests not available; cannot perform real API call")

    # Minimal OpenAI-compatible completion; adjust if needed for Deep Research endpoint
    url = os.getenv("PERPLEXITY_API_URL", "https://api.perplexity.ai/chat/completions")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a factual research assistant. Return well-structured Markdown.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    # Perplexity API returns choices similar to OpenAI
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    if not content:
        content = json.dumps(data, indent=2)
    return content


def fetch_from_jsonl(
    input_path: str, output_dir: str, model: str = "sonar-pro", dry_run: bool = True
) -> List[str]:
    """
    Read prompts from JSONL and write one Markdown output per item.

    Returns list of output file paths.
    """
    out_dir = Path(output_dir)
    _ensure_dir(out_dir)

    outputs: List[str] = []
    for obj in _read_jsonl(input_path):
        title = obj.get("title") or "Untitled"
        prompt = obj.get("prompt") or ""
        slug = slugify(title)
        out_path = out_dir / f"perplexity-output-{slug}.md"

        if dry_run:
            md = _markdown_scaffold(title=title, prompt=prompt, include_prompt=True)
        else:
            try:
                body = _call_perplexity_api(prompt=prompt, model=model)
            except Exception as e:  # pragma: no cover
                body = f"Error calling API: {e}\n\n"
            md = _markdown_scaffold(
                title=title, prompt=prompt, body=body, include_prompt=True
            )

        out_path.write_text(md, encoding="utf-8")
        outputs.append(str(out_path))

    return outputs


def main() -> None:  # pragma: no cover
    """Simple CLI wrapper for batch fetching from a JSONL file.

    Usage:
      python -m src.perplexity_fetcher --input path/to/briefs.jsonl --out out/dir --model sonar-pro --dry-run
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Perplexity Deep Research batch fetcher"
    )
    parser.add_argument(
        "--input", required=True, help="Path to JSONL file with prompts"
    )
    parser.add_argument(
        "--out", required=True, help="Directory to write Markdown outputs"
    )
    parser.add_argument(
        "--model",
        default="sonar-pro",
        help="Model name for API calls (default: sonar-pro)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate scaffolds without making API calls",
    )
    args = parser.parse_args()

    outputs = fetch_from_jsonl(
        input_path=args.input,
        output_dir=args.out,
        model=args.model,
        dry_run=args.dry_run,
    )

    for p in outputs:
        print(p)


if __name__ == "__main__":  # pragma: no cover
    main()
