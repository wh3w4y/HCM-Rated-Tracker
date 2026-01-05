from __future__ import annotations

from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .entity_base import HcmRatedTrackerEntity

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    async_add_entities([
        BookTitleText(hass, entry),
        BookAuthorText(hass, entry),
        RecommendationsText(hass, entry),
        LogText(hass, entry),
    ])

class _BaseText(HcmRatedTrackerEntity, TextEntity):
    _attr_mode = "text"
    _attr_native_max = 255

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, entry)
        self._value = ""

    @property
    def native_value(self) -> str | None:
        return self._value

    async def async_set_value(self, value: str) -> None:
        self._value = value
        self.async_write_ha_state()

class BookTitleText(_BaseText):
    _attr_name = "Book title"
    _attr_icon = "mdi:book-open-page-variant"

class BookAuthorText(_BaseText):
    _attr_name = "Author"
    _attr_icon = "mdi:account-edit"

class RecommendationsText(HcmRatedTrackerEntity, TextEntity):
    _attr_name = "Recommendations"
    _attr_icon = "mdi:lightbulb-on-outline"
    _attr_mode = "text"
    _attr_native_max = 100000

    @property
    def native_value(self) -> str | None:
        return self.manager.state.recommendations or ""

    async def async_set_value(self, value: str) -> None:
        return

class LogText(HcmRatedTrackerEntity, TextEntity):
    _attr_name = "Log"
    _attr_icon = "mdi:format-list-bulleted"
    _attr_mode = "text"
    _attr_native_max = 100000

    @property
    def native_value(self) -> str | None:
        return self.manager.format_log()

    async def async_set_value(self, value: str) -> None:
        return
