from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity

from .const import DOMAIN

class HcmRatedTrackerEntity(Entity):
    _attr_has_entity_name = True

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self._manager = hass.data[DOMAIN][entry.entry_id]

    @property
    def manager(self):
        return self._manager

    @property
    def available(self) -> bool:
        return True
