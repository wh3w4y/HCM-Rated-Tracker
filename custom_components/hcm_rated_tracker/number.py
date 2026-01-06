from __future__ import annotations

from homeassistant.components.number import NumberEntity
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
    async_add_entities([RatingNumber(store, entry.entry_id)], True)


class RatingNumber(RatedTrackerEntity, NumberEntity):
    _attr_name = "Rating"
    _attr_icon = "mdi:star-outline"
    _attr_native_min_value = 0
    _attr_native_max_value = 10
    _attr_native_step = 1
    _attr_mode = "slider"

    def __init__(self, store: RatedTrackerStore, entry_id: str) -> None:
        super().__init__(store, entry_id, "rating")

    @property
    def native_value(self) -> float:
        return float(self._store.current_rating or 0)

    async def async_set_native_value(self, value: float) -> None:
        self._store.current_rating = int(round(value))
        await self._store.async_save()
        self.async_write_ha_state()
