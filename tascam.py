import asyncio
import logging
from .const import DEFAULT_PORT

_LOGGER = logging.getLogger(__name__)

class TascamClient:
    """Async client for Tascam BD-MP4k over TCP."""
    def __init__(self, host: str, port: int = DEFAULT_PORT):
        self._host = host
        self._port = port
        self._reader: asyncio.StreamReader = None
        self._writer: asyncio.StreamWriter = None
        self._lock = asyncio.Lock()

    async def connect(self):
        """Establish a TCP connection with a short timeout."""
        try:
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port),
                timeout=1.0
            )
            _LOGGER.debug("Connected to BD-MP4k at %s:%d", self._host, self._port)
        except asyncio.TimeoutError:
            _LOGGER.warning("Timeout connecting to BD-MP4k at %s:%d", self._host, self._port)
            raise

    async def disconnect(self):
        """Close the TCP connection cleanly."""
        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()
            _LOGGER.debug("Disconnected from BD-MP4k at %s:%d", self._host, self._port)

    async def _send(self, payload: str) -> str:
        """Send a framed command and await its CR-terminated response with timeout."""
        async with self._lock:
            if self._writer is None or self._writer.is_closing():
                await self.connect()
            frame = f"!7{payload}\r"
            _LOGGER.debug("Sending: %s", frame)
            self._writer.write(frame.encode('ascii'))
            await self._writer.drain()
            try:
                response = await asyncio.wait_for(
                    self._reader.readuntil(b"\r"),
                    timeout=1.0
                )
            except asyncio.TimeoutError:
                _LOGGER.warning("Timeout waiting for response to '%s'", payload)
                # return empty or raise to let caller treat as offline
                raise
            text = response.decode('ascii', errors='ignore').strip()
            _LOGGER.debug("Received: %s", text)
            return text

    async def power_on(self):
        await self._send("PWR01")

    async def power_off(self):
        await self._send("PWR00")

    async def play(self):
        await self._send("PLY")

    async def stop(self):
        await self._send("STP")

    async def pause(self):
        await self._send("PAS")

    async def get_status(self) -> dict:
        """Fetch playback status; network reachability indicates power."""
        try:
            resp = await self._send("?SST")
            return {
                "power": True,
                "playing": resp.endswith("PL"),
                "paused": resp.endswith("PP"),
            }
        except Exception:
            return {"power": False, "playing": False, "paused": False}
