from homeassistant.const import Platform

DOMAIN = "hcm_rated_tracker"

PLATFORMS: list[Platform] = [
    Platform.TEXT,
    Platform.NUMBER,
    Platform.BUTTON,
    Platform.SENSOR,
]
