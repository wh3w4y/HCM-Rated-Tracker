from __future__ import annotations

from homeassistant.helpers.entity import Entity

from .storage import RatedTrackerStore


class RatedTrackerEntity(Entity):
    """Base entity for HCM Rated Tracker."""

    _attr_has_entity_name = True

    def __init__(self, store: RatedTrackerStore, entry_id: str, unique_suffix: str) -> None:
        self._store = store
        self._entry_id = entry_id
        self._attr_unique_id = f"{entry_id}_{unique_suffix}"
