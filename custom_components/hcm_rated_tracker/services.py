from __future__ import annotations

from datetime import datetime

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, ATTR_TITLE, ATTR_EXTRA, ATTR_RATING

SERVICE_LOG = "log_item"
SERVICE_GENERATE = "generate_recommendations"
SERVICE_RELOAD = "reload_books_yaml"

def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")

def _pick_manager(hass: HomeAssistant, entry_id: str | None):
    if entry_id:
        return hass.data.get(DOMAIN, {}).get(entry_id)
    managers = {k: v for k, v in hass.data.get(DOMAIN, {}).items() if k != "_services_registered"}
    return next(iter(managers.values()), None)

def async_register_services(hass: HomeAssistant) -> None:
    async def handle_log(call: ServiceCall) -> None:
        manager = _pick_manager(hass, call.data.get("entry_id"))
        if manager is None:
            return

        title = str(call.data.get(ATTR_TITLE, "")).strip()
        extra = str(call.data.get(ATTR_EXTRA, "")).strip()
        rating = int(call.data.get(ATTR_RATING, 0))

        if len(title) < 2 or rating < 0 or rating > 10:
            return

        await manager.add_entry(date=_today(), title=title, extra=extra, rating=rating)

    async def handle_generate(call: ServiceCall) -> None:
        manager = _pick_manager(hass, call.data.get("entry_id"))
        if manager is None:
            return
        await manager.generate_recommendations()
        await manager.save()

    async def handle_reload(call: ServiceCall) -> None:
        manager = _pick_manager(hass, call.data.get("entry_id"))
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
                vol.Required(ATTR_RATING): vol.All(vol.Coerce(int), vol.Range(min=0, max=10)),
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
        SERVICE_RELOAD,
        handle_reload,
        schema=vol.Schema({vol.Optional("entry_id"): cv.string}),
    )
