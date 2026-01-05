from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    CONF_PRESET,
    CONF_TRACKER_NAME,
    CONF_ITEM_LABEL,
    CONF_EXTRA_LABEL,
    CONF_MIN_RATING,
    CONF_RECENT_COUNT,
    CONF_SAME_LANE_COUNT,
    CONF_DIFFERENT_GENRE_COUNT,
    CONF_OPENAI_CONFIG_ENTRY,
    DEFAULT_MIN_RATING,
    DEFAULT_RECENT_COUNT,
    DEFAULT_SAME_LANE_COUNT,
    DEFAULT_DIFFERENT_GENRE_COUNT,
)
from .storage import TrackerStorage, RatedEntry, TrackerState
from .services import async_register_services

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["text", "number", "button"]


class TrackerManager:
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.storage = TrackerStorage(hass, entry.entry_id)
        self.state = TrackerState()

        self.current_title: str = ""
        self.current_extra: str = ""
        self.current_rating: int = 0

    @property
    def opts(self) -> dict:
        o = self.entry.options
        d = self.entry.data
        return {
            CONF_PRESET: str(o.get(CONF_PRESET, d.get(CONF_PRESET, "other"))),
            CONF_TRACKER_NAME: str(o.get(CONF_TRACKER_NAME, d.get(CONF_TRACKER_NAME, "Tracker"))),
            CONF_ITEM_LABEL: str(o.get(CONF_ITEM_LABEL, d.get(CONF_ITEM_LABEL, "item"))),
            CONF_EXTRA_LABEL: str(o.get(CONF_EXTRA_LABEL, d.get(CONF_EXTRA_LABEL, "Extra"))),
            CONF_MIN_RATING: int(o.get(CONF_MIN_RATING, DEFAULT_MIN_RATING)),
            CONF_RECENT_COUNT: int(o.get(CONF_RECENT_COUNT, DEFAULT_RECENT_COUNT)),
            CONF_SAME_LANE_COUNT: int(o.get(CONF_SAME_LANE_COUNT, DEFAULT_SAME_LANE_COUNT)),
            CONF_DIFFERENT_GENRE_COUNT: int(o.get(CONF_DIFFERENT_GENRE_COUNT, DEFAULT_DIFFERENT_GENRE_COUNT)),
            CONF_OPENAI_CONFIG_ENTRY: str(o.get(CONF_OPENAI_CONFIG_ENTRY, "")).strip(),
        }

    def _fire_update(self) -> None:
        self.hass.bus.async_fire(f"{DOMAIN}_updated_{self.entry.entry_id}")

    async def load(self) -> None:
        self.state = await self.storage.load()

    async def add_entry(self, date: str, title: str, extra: str, rating: int) -> None:
        self.state.entries.insert(0, RatedEntry(date=date, title=title, extra=extra, rating=rating))
        self.state.entries = self.state.entries[:500]
        await self.storage.save(self.state)
        self._fire_update()

    def format_log(self) -> str:
        extra_label = self.opts[CONF_EXTRA_LABEL]
        lines = []
        for e in self.state.entries:
            extra_part = f" — {extra_label}: {e.extra}" if e.extra else ""
            lines.append(f'{e.date} — "{e.title}"{extra_part} — {e.rating}/10')
        return "\n".join(lines)

    def _build_prompt(self) -> str:
        o = self.opts
        min_rating = o[CONF_MIN_RATING]
        recent_n = o[CONF_RECENT_COUNT]
        same_n = o[CONF_SAME_LANE_COUNT]
        diff_n = o[CONF_DIFFERENT_GENRE_COUNT]
        item_label = o[CONF_ITEM_LABEL]
        extra_label = o[CONF_EXTRA_LABEL]

        lines = self.format_log().split("\n") if self.state.entries else []
        recent_any = "\n".join(lines[:recent_n])

        high = []
        for e in self.state.entries:
            if e.rating >= min_rating:
                extra_part = f" — {extra_label}: {e.extra}" if e.extra else ""
                high.append(f'{e.date} — "{e.title}"{extra_part} — {e.rating}/10')
        high_text = "\n".join(high[:200])

        return f"""You are a recommendation assistant for {item_label}s.

Each line is: YYYY-MM-DD — "Title" — {extra_label}: (optional) — X/10

TASK A — Recent genre(s):
From the RECENT LIST (any ratings), infer what genre(s) have been consumed lately for these {item_label}s.
Output:
- "Recent genre(s): ..." (1–3 genres)
- "Why: ..." (1 short sentence)

TASK B — Recommendations in the current lane:
Using ONLY the HIGH-RATED LIST (rated {min_rating}/10 or above) as the taste profile,
recommend {same_n} {item_label}s that match the RECENT genre(s).
For each: Title — {extra_label} (if relevant) — 1 short reason.
Avoid repeating items already listed.

TASK C — Recommendations outside the lane:
Recommend {diff_n} {item_label}s from DIFFERENT genres than the RECENT genre(s), but still likely to fit the taste profile.
For each: Title — {extra_label} (if relevant) — Genre — 1 short reason.

OUTPUT FORMAT (exact):
Recent genre(s): ...
Why: ...

Same-lane picks:
- ...
- ...

Different-genre picks:
- ...
- ...

DATA — RECENT LIST:
{recent_any}

DATA — HIGH-RATED LIST ({min_rating}/10+):
{high_text}
""".strip()

    async def generate_recommendations(self) -> None:
        openai_entry = self.opts[CONF_OPENAI_CONFIG_ENTRY]
        if not openai_entry:
            self.state.recommendations = "OpenAI config_entry not set. Configure HCM Rated Tracker options."
            await self.storage.save(self.state)
            self._fire_update()
            return

        prompt = self._build_prompt()

        try:
            response = await self.hass.services.async_call(
                "openai_conversation",
                "generate_content",
                {"config_entry": openai_entry, "prompt": prompt},
                blocking=True,
                return_response=True,
            )
        except Exception as err:
            _LOGGER.exception("OpenAI generate_content failed: %s", err)
            self.state.recommendations = f"AI error: {err}"
            await self.storage.save(self.state)
            self._fire_update()
            return

        text = ""
        if isinstance(response, dict):
            text = (response.get("text") or response.get("content") or response.get("response") or "").strip()
        if not text:
            text = str(response).strip()

        self.state.recommendations = text
        await self.storage.save(self.state)
        self._fire_update()


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    manager = TrackerManager(hass, entry)
    await manager.load()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = manager

    if not hass.data[DOMAIN].get("_services_registered"):
        async_register_services(hass)
        hass.data[DOMAIN]["_services_registered"] = True

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return ok
