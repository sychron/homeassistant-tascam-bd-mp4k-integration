"""Tascam BD-MP4k integration."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .tascam import TascamClient

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the integration and store the client."""
    host = entry.data["host"]
    port = entry.data["port"]
    client = TascamClient(host, port)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = client
    await hass.config_entries.async_forward_entry_setups(entry, ["media_player"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload integration and disconnect the client."""
    client = hass.data[DOMAIN].pop(entry.entry_id)
    await client.disconnect()
    return await hass.config_entries.async_forward_entry_unload(entry, "media_player")
