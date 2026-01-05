from __future__ import annotations

from datetime import datetime

import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, ATTR_TITLE, ATTR_EXTRA, ATTR_RATING


SERVICE_LOG = "log_item"
SERVICE_GENERATE = "generate_recommendations"
SERVICE_RELOAD_YAML = "reload_books_yaml"


def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def async_register_services(hass: HomeAssistant) -> None:
    async def _get_manager(entry_id: str | None):
        if entry_id:
            return hass.data[DOMAIN].get(entry_id)
        # first real entry (ignore marker)
        for k, v in hass.data[DOMAIN].items():
            if k != "_services_registered":
                return v
        return None

    async def handle_log(call) -> None:
        manager = await _get_manager(call.data.get("entry_id"))
        if manager is None:
            return

        title = str(call.data.get(ATTR_TITLE, "")).strip()
        extra = str(call.data.get(ATTR_EXTRA, "")).strip()
        rating = int(call.data.get(ATTR_RATING, 0))
        if len(title) < 1 or rating < 1 or rating > 10:
            return

        await manager.add_entry(date=_today(), title=title, extra=extra, rating=rating, persist_yaml=True)
        await manager.generate_recommendations()

    async def handle_generate(call) -> None:
        manager = await _get_manager(call.data.get("entry_id"))
        if manager is None:
            return
        await manager.generate_recommendations()

    async def handle_reload_yaml(call) -> None:
        manager = await _get_manager(call.data.get("entry_id"))
        if manager is None:
            return
        await manager.reload_from_yaml()

    hass.services.async_register(
        DOMAIN,
        SERVICE_LOG,
        handle_log,
        schema=vol.Schema(
            {
                vol.Optional("entry_id"): cv.string,
                vol.Required(ATTR_TITLE): cv.string,
                vol.Optional(ATTR_EXTRA, default=""): cv.string,
                vol.Required(ATTR_RATING): vol.All(vol.Coerce(int), vol.Range(min=1, max=10)),
            }
        ),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_GENERATE,
        handle_generate,
        schema=vol.Schema({vol.Optional("entry_id"): cv.string}),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_RELOAD_YAML,
        handle_reload_yaml,
        schema=vol.Schema({vol.Optional("entry_id"): cv.string}),
    )
