from __future__ import annotations

from homeassistant.components.number import NumberEntity

from .entity_base import TrackerEntity


class RatingNumber(TrackerEntity, NumberEntity):
    _attr_icon = "mdi:star"
    _attr_native_min_value = 1
    _attr_native_max_value = 10
    _attr_native_step = 1
    _attr_mode = "slider"

    def __init__(self, manager):
        super().__init__(manager, "Rating", "draft_rating")

    @property
    def native_value(self) -> float | None:
        return float(self.manager.draft_rating or 5)

    async def async_set_native_value(self, value: float) -> None:
        self.manager.draft_rating = int(round(value))
        self.async_write_ha_state()


async def async_setup_entry(hass, entry, async_add_entities):
    manager = hass.data["hcm_rated_tracker"][entry.entry_id]
    async_add_entities([RatingNumber(manager)], True)
