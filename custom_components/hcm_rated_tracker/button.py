from __future__ import annotations

from homeassistant.components.button import ButtonEntity
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
    async_add_entities([AddEntryButton(store, entry.entry_id)], True)


class AddEntryButton(RatedTrackerEntity, ButtonEntity):
    _attr_name = "Add Entry"
    _attr_icon = "mdi:playlist-plus"

    def __init__(self, store: RatedTrackerStore, entry_id: str) -> None:
        super().__init__(store, entry_id, "add_entry")

    async def async_press(self) -> None:
        await self._store.async_add_entry()
        # Ask HA to refresh sensor state as well
        self.async_write_ha_state()
