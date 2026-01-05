from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .yaml_store import YamlStore, RatedEntry, TrackerState

class TrackerManager:
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.store = YamlStore(hass)
        self.state = TrackerState()

    async def load(self) -> None:
        self.state = await self.store.load()
        await self.generate_recommendations()

    async def save(self) -> None:
        await self.store.save(self.state)

    async def reload_from_yaml(self) -> None:
        self.state = await self.store.load()
        await self.generate_recommendations()

    async def add_entry(self, date: str, title: str, extra: str, rating: int) -> None:
        title = title.strip()
        extra = extra.strip()

        current = await self.store.load()

        def key(e: RatedEntry) -> tuple[str, str]:
            return (e.title.strip().lower(), e.extra.strip().lower())

        new_e = RatedEntry(date=date, title=title, extra=extra, rating=int(rating))

        # update/insert
        found = False
        updated: list[RatedEntry] = []
        for e in current.entries:
            if key(e) == key(new_e):
                updated.append(new_e)
                found = True
            else:
                updated.append(e)
        if not found:
            updated.insert(0, new_e)

        current.entries = updated
        self.state = current

        await self.generate_recommendations()
        await self.save()

    async def generate_recommendations(self) -> None:
        entries = self.state.entries
        if not entries:
            self.state.recommendations = "Add some books and tap Recommend to see suggestions."
            return

        top = [e for e in entries if e.rating >= 9]
        mid = [e for e in entries if 7 <= e.rating <= 8]
        low = [e for e in entries if e.rating <= 6]

        authors_top: dict[str, int] = {}
        for e in top:
            if e.extra:
                authors_top[e.extra] = authors_top.get(e.extra, 0) + 1

        fav_authors = sorted(authors_top.items(), key=lambda kv: kv[1], reverse=True)[:3]
        fav_authors_txt = ", ".join([a for a, _ in fav_authors]) if fav_authors else "—"

        lines: list[str] = []
        lines.append(f"Books logged: {len(entries)}")
        lines.append(f"Top-rated (9–10): {len(top)} | Mid (7–8): {len(mid)} | Low (0–6): {len(low)}")
        lines.append(f"Favourite author(s): {fav_authors_txt}")
        if top:
            lines.append("Try more like your 9–10s: search for similar authors/series or the same genre.")
        if low:
            lines.append("Low-rated books can help: note what you disliked in the Author field or a tag.")
        self.state.recommendations = "\n".join(lines)

    def format_log(self, limit: int = 50) -> str:
        if not self.state.entries:
            return "No books logged yet."
        out = []
        for e in self.state.entries[:limit]:
            author = f" — {e.extra}" if e.extra else ""
            out.append(f"{e.date} • {e.title}{author} • {e.rating}/10")
        if len(self.state.entries) > limit:
            out.append(f"... ({len(self.state.entries) - limit} more)")
        return "\n".join(out)
