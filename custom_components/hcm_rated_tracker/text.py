from __future__ import annotations

from homeassistant.components.text import TextEntity

from .entity_base import TrackerEntity


class DraftTitleText(TrackerEntity, TextEntity):
    _attr_icon = "mdi:book-edit"
    _attr_native_max = 200

    def __init__(self, manager):
        super().__init__(manager, "Book title", "draft_title")

    @property
    def native_value(self) -> str | None:
        return self.manager.draft_title or ""

    async def async_set_value(self, value: str) -> None:
        self.manager.draft_title = (value or "").strip()
        self.async_write_ha_state()


class DraftAuthorText(TrackerEntity, TextEntity):
    _attr_icon = "mdi:account-edit"
    _attr_native_max = 200

    def __init__(self, manager):
        super().__init__(manager, "Author", "draft_author")

    @property
    def native_value(self) -> str | None:
        return self.manager.draft_extra or ""

    async def async_set_value(self, value: str) -> None:
        self.manager.draft_extra = (value or "").strip()
        self.async_write_ha_state()


class RecommendationsText(TrackerEntity, TextEntity):
    _attr_icon = "mdi:lightbulb-outline"
    _attr_native_max = 100000
    _attr_mode = "text"
    _attr_entity_category = None

    def __init__(self, manager):
        super().__init__(manager, "Recommendations", "recommendations")

    @property
    def native_value(self) -> str | None:
        return self.manager.state.recommendations or "Tap Recommend to generate suggestions."

    async def async_set_value(self, value: str) -> None:
        # read-only in UI
        return


class LogText(TrackerEntity, TextEntity):
    _attr_icon = "mdi:format-list-bulleted"
    _attr_native_max = 100000
    _attr_mode = "text"

    def __init__(self, manager):
        super().__init__(manager, "Log", "log")

    @property
    def native_value(self) -> str | None:
        return self.manager.format_log()

    async def async_set_value(self, value: str) -> None:
        # read-only in UI
        return


async def async_setup_entry(hass, entry, async_add_entities):
    manager = hass.data["hcm_rated_tracker"][entry.entry_id]
    async_add_entities(
        [
            DraftTitleText(manager),
            DraftAuthorText(manager),
            RecommendationsText(manager),
            LogText(manager),
        ],
        True,
    )
