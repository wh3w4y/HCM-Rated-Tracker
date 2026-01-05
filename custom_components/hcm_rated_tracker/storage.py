from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import STORAGE_VERSION, DOMAIN


@dataclass
class RatedEntry:
    date: str
    title: str
    extra: str
    rating: int


@dataclass
class TrackerState:
    entries: list[RatedEntry] = field(default_factory=list)  # newest first
    recommendations: str = ""


class TrackerStorage:
    def __init__(self, hass: HomeAssistant, entry_id: str) -> None:
        key = f"{DOMAIN}.storage.{entry_id}"
        self._store = Store(hass, STORAGE_VERSION, key)

    async def load(self) -> TrackerState:
        data = await self._store.async_load()
        if not data:
            return TrackerState()

        entries: list[RatedEntry] = []
        for e in data.get("entries", []):
            entries.append(
                RatedEntry(
                    date=str(e.get("date", "")),
                    title=str(e.get("title", "")),
                    extra=str(e.get("extra", "")),
                    rating=int(e.get("rating", 0)),
                )
            )

        return TrackerState(entries=entries, recommendations=str(data.get("recommendations", "")))

    async def save(self, state: TrackerState) -> None:
        payload: dict[str, Any] = {
            "entries": [
                {"date": e.date, "title": e.title, "extra": e.extra, "rating": e.rating}
                for e in state.entries
            ],
            "recommendations": state.recommendations,
        }
        await self._store.async_save(payload)
