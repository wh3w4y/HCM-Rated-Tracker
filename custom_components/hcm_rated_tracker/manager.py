from __future__ import annotations

from dataclasses import replace
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .books_yaml import load_books_yaml, save_books_yaml
from .const import SIGNAL_UPDATED
from .storage import RatedEntry, TrackerState, TrackerStorage


class TrackerManager:
    def __init__(self, hass: HomeAssistant, entry_id: str) -> None:
        self.hass = hass
        self.entry_id = entry_id
        self.storage = TrackerStorage(hass, entry_id)
        self.state = TrackerState()

        # Draft fields (edited via entities)
        self.draft_title: str = ""
        self.draft_extra: str = ""
        self.draft_rating: int = 5

    async def load(self) -> None:
        self.state = await self.storage.load()
        # keep drafts sane
        if self.draft_rating < 1 or self.draft_rating > 10:
            self.draft_rating = 5
        async_dispatcher_send(self.hass, SIGNAL_UPDATED, self.entry_id)

    async def save_state(self) -> None:
        await self.storage.save(self.state)
        async_dispatcher_send(self.hass, SIGNAL_UPDATED, self.entry_id)

    async def reload_from_yaml(self) -> None:
        yaml_entries = load_books_yaml(self.hass)
        if yaml_entries is None:
            return
        self.state.entries = [
            RatedEntry(date=e["date"], title=e["title"], extra=e["extra"], rating=e["rating"])
            for e in yaml_entries
        ]
        # recommendations will be regenerated on demand
        self.state.recommendations = ""
        await self.save_state()

    def format_log(self, limit: int = 50) -> str:
        if not self.state.entries:
            return "No books logged yet."
        lines = []
        for e in self.state.entries[:limit]:
            author = e.extra.strip() or "Unknown"
            lines.append(f"{e.date} — {e.title} ({author}) — {e.rating}/10")
        return "\n".join(lines)

    async def add_entry(self, date: str, title: str, extra: str, rating: int, persist_yaml: bool = False) -> None:
        new = RatedEntry(date=date, title=title, extra=extra, rating=rating)
        # newest first, avoid exact duplicates
        entries = [new] + [
            e for e in self.state.entries
            if not (e.date == new.date and e.title == new.title and e.extra == new.extra and e.rating == new.rating)
        ]
        self.state.entries = entries
        await self.save_state()

        if persist_yaml:
            # If YAML exists OR user wants YAML, write it (creates folder/file)
            payload = [
                {"date": e.date, "title": e.title, "extra": e.extra, "rating": e.rating}
                for e in self.state.entries
            ]
            save_books_yaml(self.hass, payload)

    async def commit_draft(self) -> None:
        title = (self.draft_title or "").strip()
        if not title:
            return
        extra = (self.draft_extra or "").strip()
        rating = int(self.draft_rating or 0)
        if rating < 1 or rating > 10:
            return
        today = self.hass.config.time_zone  # unused, keep lint happy
        from homeassistant.util.dt import now
        d = now(self.hass).date().isoformat()
        await self.add_entry(date=d, title=title, extra=extra, rating=rating, persist_yaml=True)

        # clear drafts (optional)
        self.draft_title = ""
        self.draft_extra = ""
        self.draft_rating = 5
        async_dispatcher_send(self.hass, SIGNAL_UPDATED, self.entry_id)

    async def generate_recommendations(self) -> None:
        if not self.state.entries:
            self.state.recommendations = "Log a few books first, then tap Recommend."
            await self.save_state()
            return

        # Simple heuristics: highlight favorite authors and high ratings
        top = sorted(self.state.entries, key=lambda e: e.rating, reverse=True)[:10]
        authors: dict[str, int] = {}
        for e in self.state.entries:
            a = (e.extra or "").strip()
            if a:
                authors[a] = authors.get(a, 0) + 1
        top_authors = sorted(authors.items(), key=lambda kv: kv[1], reverse=True)[:3]

        avg = sum(e.rating for e in self.state.entries) / max(1, len(self.state.entries))
        lines = []
        lines.append(f"Average rating: {avg:.1f}/10")
        if top_authors:
            lines.append("Most-read author(s): " + ", ".join([f"{a} ({n})" for a, n in top_authors]))
        lines.append("Top recent picks:")
        for e in top[:5]:
            a = e.extra.strip() or "Unknown"
            lines.append(f"• {e.title} — {a} — {e.rating}/10")
        lines.append("")
        lines.append("Suggestion: pick another book by a top author, or a similar genre to your 9–10/10 reads.")
        self.state.recommendations = "\n".join(lines)
        await self.save_state()
