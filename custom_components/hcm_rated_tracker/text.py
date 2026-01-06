from __future__ import annotations

from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity_base import HcmRatedTrackerEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities(
        [
            BookTitleText(hass, entry),
            BookAuthorText(hass, entry),
            RecommendationsText(hass, entry),
            LogText(hass, entry),
        ],
        True,
    )


class BookTitleText(HcmRatedTrackerEntity, TextEntity):
    _attr_name = "Book title"
    _attr_icon = "mdi:book-open-page-variant"
    _attr_mode = "text"
    _attr_native_max = 255

    @property
    def native_value(self) -> str | None:
        return getattr(self.manager, "book_title", "") or ""

    async def async_set_value(self, value: str) -> None:
        # Prefer manager method if it exists, otherwise set attribute
        if hasattr(self.manager, "set_book_title"):
            await self.manager.set_book_title(value)
        else:
            self.manager.book_title = value
            self.async_write_ha_state()


class BookAuthorText(HcmRatedTrackerEntity, TextEntity):
    _attr_name = "Author"
    _attr_icon = "mdi:account-edit"
    _attr_mode = "text"
    _attr_native_max = 255

    @property
    def native_value(self) -> str | None:
        return getattr(self.manager, "author", "") or ""

    async def async_set_value(self, value: str) -> None:
        if hasattr(self.manager, "set_author"):
            await self.manager.set_author(value)
        else:
            self.manager.author = value
            self.async_write_ha_state()


class RecommendationsText(HcmRatedTrackerEntity, TextEntity):
    _attr_name = "Recommendations"
    _attr_icon = "mdi:lightbulb-on-outline"
    _attr_mode = "text"
    _attr_native_max = 100000

    @property
    def native_value(self) -> str | None:
        return getattr(self.manager.state, "recommendations", "") or ""

    async def async_set_value(self, value: str) -> None:
        # Read-only
        return


class LogText(HcmRatedTrackerEntity, TextEntity):
    _attr_name = "Log"
    _attr_icon = "mdi:format-list-bulleted"
    _attr_mode = "text"
    _attr_native_max = 100000

    @property
    def native_value(self) -> str | None:
        if hasattr(self.manager, "format_log"):
            return self.manager.format_log()
        return ""

    async def async_set_value(self, value: str) -> None:
        # Read-only
        return
