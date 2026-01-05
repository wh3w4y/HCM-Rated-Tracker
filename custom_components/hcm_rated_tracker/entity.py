from __future__ import annotations

from homeassistant.helpers.entity import Entity
from .const import DOMAIN


class BaseTrackerEntity(Entity):
    _attr_has_entity_name = True

    def __init__(self, entry_id: str) -> None:
        self._entry_id = entry_id

    @property
    def unique_id(self) -> str:
        return f"{DOMAIN}_{self._entry_id}_{self._attr_name}".lower().replace(" ", "_")
