import logging
from datetime import timedelta
from homeassistant.components.media_player import MediaPlayerEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.const import STATE_OFF, STATE_PLAYING, STATE_PAUSED, STATE_IDLE
from .const import DOMAIN, SUPPORT_TASCAM

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    client = hass.data[DOMAIN][entry.entry_id]
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{entry.title} status",
        update_method=client.get_status,
        update_interval=timedelta(seconds=30),
    )
    # Add entity immediately without waiting for first refresh
    async_add_entities([TascamMediaPlayer(coordinator, client, entry)], False)


class TascamMediaPlayer(MediaPlayerEntity):
    """Media player representation of the Tascam BD-MP4k."""

    def __init__(self, coordinator, client, entry):
        self.coordinator = coordinator
        self._client = client
        self._entry = entry

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    @property
    def name(self) -> str:
        return self._entry.title

    @property
    def unique_id(self) -> str:
        return self._entry.entry_id

    @property
    def state(self) -> str:
        data = self.coordinator.data or {}
        if not data.get("power"):
            return STATE_OFF
        if data.get("playing"):
            return STATE_PLAYING
        if data.get("paused"):
            return STATE_PAUSED
        return STATE_IDLE

    @property
    def supported_features(self) -> int:
        return SUPPORT_TASCAM

    async def async_update(self) -> None:
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self) -> None:
        await self._client.power_on()

    async def async_turn_off(self) -> None:
        await self._client.power_off()

    async def async_media_play(self) -> None:
        await self._client.play()

    async def async_media_pause(self) -> None:
        await self._client.pause()

    async def async_media_stop(self) -> None:
        await self._client.stop()
