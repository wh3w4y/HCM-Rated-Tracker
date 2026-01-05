from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, ATTR_TITLE, ATTR_EXTRA, ATTR_RATING

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    async_add_entities([
        SaveButton(hass, entry),
        RecommendButton(hass, entry),
        ReloadYamlButton(hass, entry),
    ])

def _get_entities(hass: HomeAssistant, entry_id: str) -> dict[str, str]:
    ent_reg = hass.helpers.entity_registry.async_get(hass)
    out: dict[str, str] = {}
    for ent in ent_reg.entities.values():
        if ent.config_entry_id != entry_id:
            continue
        if ent.original_name == "Book title":
            out["title"] = ent.entity_id
        elif ent.original_name == "Author":
            out["author"] = ent.entity_id
        elif ent.original_name == "Rating":
            out["rating"] = ent.entity_id
    return out

class _BaseButton(ButtonEntity):
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry

    @property
    def manager(self):
        return self.hass.data[DOMAIN][self.entry.entry_id]

class SaveButton(_BaseButton):
    _attr_name = "Save"
    _attr_icon = "mdi:content-save"

    async def async_press(self) -> None:
        ids = _get_entities(self.hass, self.entry.entry_id)

        st_title = self.hass.states.get(ids.get("title", ""))
        st_author = self.hass.states.get(ids.get("author", ""))
        st_rating = self.hass.states.get(ids.get("rating", ""))

        title = st_title.state if st_title else ""
        author = st_author.state if st_author else ""
        rating = 0
        if st_rating and st_rating.state not in ("unknown", "unavailable"):
            try:
                rating = int(float(st_rating.state))
            except Exception:
                rating = 0

        await self.hass.services.async_call(
            DOMAIN,
            "log_item",
            {
                "entry_id": self.entry.entry_id,
                ATTR_TITLE: title,
                ATTR_EXTRA: author,
                ATTR_RATING: rating,
            },
            blocking=True,
        )

class RecommendButton(_BaseButton):
    _attr_name = "Recommend"
    _attr_icon = "mdi:wand"

    async def async_press(self) -> None:
        await self.hass.services.async_call(
            DOMAIN,
            "generate_recommendations",
            {"entry_id": self.entry.entry_id},
            blocking=True,
        )

class ReloadYamlButton(_BaseButton):
    _attr_name = "Reload YAML"
    _attr_icon = "mdi:reload"

    async def async_press(self) -> None:
        await self.hass.services.async_call(
            DOMAIN,
            "reload_books_yaml",
            {"entry_id": self.entry.entry_id},
            blocking=True,
        )
