from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import yaml
from homeassistant.core import HomeAssistant
from homeassistant.util.dt import now

DEFAULT_REL_PATH = "hcm_rated_tracker/books.yaml"


def _today_iso(hass: HomeAssistant) -> str:
    return now(hass).date().isoformat()


def load_books_yaml(
    hass: HomeAssistant,
    rel_path: str = DEFAULT_REL_PATH,
) -> list[dict[str, Any]] | None:
    """
    Load /config/hcm_rated_tracker/books.yaml (if it exists) and return entries in
    the integration's storage schema:
      { "date": "YYYY-MM-DD", "title": "...", "extra": "author", "rating": 0-10 }

    If the YAML file does not exist, returns None (so existing .storage behaviour remains).
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
        # Support both 'author' (friendly) and 'extra' (internal)
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

    return out
