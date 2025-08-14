from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any
import re


@dataclass
class ImportItem:
    title: str
    url: str
    source: str
    saved_at: datetime
    type: str = "literature"
    topics: List[str] = None

    def key(self) -> str:
        """Unique key based on (url, saved_at ISO date-time)."""
        return f"{self.url}::{self.saved_at.isoformat()}"


_ISO_DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})")


def _parse_saved_at(value: str | None) -> datetime:
    if not value:
        return datetime.now()
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        m = _ISO_DATE_RE.match(value)
        if m:
            try:
                return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            except Exception:
                pass
    return datetime.now()


def _coerce_topics(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    s = str(value)
    if "," in s:
        return [t.strip() for t in s.split(",") if t.strip()]
    return [s.strip()] if s.strip() else []


def validate_item(data: Dict[str, Any]) -> ImportItem:
    """Validate incoming row dict and coerce to ImportItem.

    Required: title, url, source, saved_at (coerced), topics (coerced) optional.
    """
    title = (data.get("title") or "").strip()
    url = (data.get("url") or "").strip()
    source = (data.get("source") or "").strip()
    saved_at_raw = (data.get("saved_at") or data.get("date") or "").strip()
    if not title or not url:
        raise ValueError("Missing required fields: title and url")
    saved_at = _parse_saved_at(saved_at_raw)
    topics = _coerce_topics(data.get("topics"))
    return ImportItem(
        title=title,
        url=url,
        source=source or "unknown",
        saved_at=saved_at,
        type="literature",
        topics=topics,
    )
