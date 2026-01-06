from __future__ import annotations

from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import RatedTrackerEntity
from .storage import RatedTrackerStore


def _store(hass: HomeAssistant, entry: ConfigEntry) -> RatedTrackerStore:
    return hass.data[DOMAIN][entry.entry_id]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    store = _store(hass, entry)

    async_add_entities(
        [
            BookTitleText(store, entry.entry_id),
            AuthorText(store, entry.entry_id),
        ],
        True,
    )


class BookTitleText(RatedTrackerEntity, TextEntity):
    _attr_name = "Book Title"
    _attr_icon = "mdi:book-open-variant"
    _attr_native_max = 200

    def __init__(self, store: RatedTrackerStore, entry_id: str) -> None:
        super().__init__(store, entry_id, "book_title")

    @property
    def native_value(self) -> str:
        return self._store.current_title

    async def async_set_value(self, value: str) -> None:
        self._store.current_title = value
        await self._store.async_save()
        self.async_write_ha_state()


class AuthorText(RatedTrackerEntity, TextEntity):
    _attr_name = "Author"
    _attr_icon = "mdi:account-edit"
    _attr_native_max = 200

    def __init__(self, store: RatedTrackerStore, entry_id: str) -> None:
        super().__init__(store, entry_id, "author")

    @property
    def native_value(self) -> str:
        return self._store.current_author

    async def async_set_value(self, value: str) -> None:
        self._store.current_author = value
        await self._store.async_save()
        self.async_write_ha_state()
