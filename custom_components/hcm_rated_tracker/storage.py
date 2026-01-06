from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

STORAGE_VERSION = 1


@dataclass
class RatedEntry:
    title: str
    author: str
    rating: int
    date: str


class RatedTrackerStore:
    """Simple per-config-entry storage for rated books."""

    def __init__(self, hass: HomeAssistant, entry_id: str) -> None:
        self.hass = hass
        self._store = Store(hass, STORAGE_VERSION, f"hcm_rated_tracker.{entry_id}")
        self.entries: list[RatedEntry] = []
        self.current_title: str = ""
        self.current_author: str = ""
        self.current_rating: int = 0
        self.log: str = ""
        self._listeners: list[callable] = []

    async def async_load(self) -> None:
        data = await self._store.async_load()
        if not data:
            return

        self.current_title = data.get("current_title", "")
        self.current_author = data.get("current_author", "")
        self.current_rating = int(data.get("current_rating", 0) or 0)
        self.log = data.get("log", "")

        raw_entries = data.get("entries", []) or []
        self.entries = [
            RatedEntry(
                title=str(e.get("title", "")),
                author=str(e.get("author", "")),
                rating=int(e.get("rating", 0) or 0),
                date=str(e.get("date", "")),
            )
            for e in raw_entries
        ]

    async def async_save(self) -> None:
        await self._store.async_save(
            {
                "current_title": self.current_title,
                "current_author": self.current_author,
                "current_rating": self.current_rating,
                "log": self.log,
                "entries": [
                    {"title": e.title, "author": e.author, "rating": e.rating, "date": e.date}
                    for e in self.entries
                ],
            }
        )
for cb in list(self._listeners):
    try:
        cb()
    except Exception:
        # Avoid breaking the integration if a listener misbehaves
        pass


    async def async_add_entry(self) -> RatedEntry | None:
        title = (self.current_title or "").strip()
        author = (self.current_author or "").strip()
        rating = int(self.current_rating or 0)

        if not title:
            self.log = self._append_log("❌ No title entered — nothing added.")
            await self.async_save()
            return None

        new_entry = RatedEntry(
            title=title,
            author=author,
            rating=rating,
            date=date.today().isoformat(),
        )
        self.entries.insert(0, new_entry)

        line = f"✅ Added: {new_entry.title} — {new_entry.author or 'Unknown'} — {new_entry.rating}/10 — {new_entry.date}"
        self.log = self._append_log(line)

        self.current_title = ""
        self.current_author = ""
        self.current_rating = 0

        await self.async_save()
        return new_entry

def add_listener(self, cb) -> callable:
    """Register a callback to be called after data changes. Returns an unsubscribe."""
    self._listeners.append(cb)

    def _remove():
        if cb in self._listeners:
            self._listeners.remove(cb)

    return _remove

    def _append_log(self, line: str) -> str:
        existing = self.log or ""
        return f"{line}\n{existing}" if existing else line
