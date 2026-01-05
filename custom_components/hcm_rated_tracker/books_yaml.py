from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import yaml
from homeassistant.core import HomeAssistant
from homeassistant.util.dt import now

from .const import DEFAULT_YAML_REL_PATH


def _today_iso(hass: HomeAssistant) -> str:
    return now(hass).date().isoformat()


def load_books_yaml(
    hass: HomeAssistant,
    rel_path: str = DEFAULT_YAML_REL_PATH,
) -> list[dict[str, Any]] | None:
    """Load /config/hcm_rated_tracker/books.yaml (if it exists).

    Returns list of dicts with schema:
      { "date": "YYYY-MM-DD", "title": "...", "extra": "author", "rating": 0-10 }

    If the YAML file does not exist, returns None.
    """
    path = Path(hass.config.path(rel_path))
    if not path.exists():
        return None

    raw = path.read_text(encoding="utf-8")
    data = yaml.safe_load(raw) or {}

    if not isinstance(data, dict):
        raise ValueError("books.yaml must be a mapping with a top-level 'entries' key")

    entries = data.get("entries", [])
    if not isinstance(entries, list):
        raise ValueError("'entries' in books.yaml must be a list")

    out: list[dict[str, Any]] = []

    for i, item in enumerate(entries):
        if not isinstance(item, dict):
            raise ValueError(f"Entry #{i+1} must be a mapping")

        title = str(item.get("title", "")).strip()
        author = str(item.get("author", item.get("extra", ""))).strip()
        rating = item.get("rating", 0)
        entry_date = str(item.get("date", "")).strip() or _today_iso(hass)

        if not title:
            raise ValueError(f"Entry #{i+1} is missing 'title'")

        try:
            rating_int = int(rating)
        except Exception as e:
            raise ValueError(f"Entry #{i+1} has invalid rating: {rating}") from e

        if rating_int < 0 or rating_int > 10:
            raise ValueError(f"Entry #{i+1} rating must be 0-10 (got {rating_int})")

        try:
            date.fromisoformat(entry_date)
        except Exception as e:
            raise ValueError(f"Entry #{i+1} date must be YYYY-MM-DD (got {entry_date})") from e

        out.append(
            {
                "date": entry_date,
                "title": title,
                "extra": author,
                "rating": rating_int,
            }
        )

    # newest first
    out.sort(key=lambda e: e["date"], reverse=True)
    return out


def save_books_yaml(
    hass: HomeAssistant,
    entries: list[dict[str, Any]],
    rel_path: str = DEFAULT_YAML_REL_PATH,
) -> None:
    """Write entries back to /config/hcm_rated_tracker/books.yaml.

    Writes friendly keys: date/title/author/rating
    """
    path = Path(hass.config.path(rel_path))
    path.parent.mkdir(parents=True, exist_ok=True)

    # newest first
    sorted_entries = sorted(entries, key=lambda e: str(e.get("date", "")), reverse=True)

    payload = {
        "entries": [
            {
                "date": str(e.get("date", "")).strip(),
                "title": str(e.get("title", "")).strip(),
                "author": str(e.get("extra", "")).strip(),
                "rating": int(e.get("rating", 0)),
            }
            for e in sorted_entries
        ]
    }
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")
