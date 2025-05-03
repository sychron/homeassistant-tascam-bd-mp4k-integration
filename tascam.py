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
        self._reader, self._writer = await asyncio.open_connection(self._host, self._port)

    async def disconnect(self):
        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()

    async def _send(self, payload: str) -> str:
        async with self._lock:
            if self._writer is None or self._writer.is_closing():
                await self.connect()
            msg = f"!7{payload}\r"
            self._writer.write(msg.encode('ascii'))
            await self._writer.drain()
            data = await self._reader.readuntil(b"\r")
            return data.decode('ascii', errors='ignore').strip()

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
        try:
            resp = await self._send("?SST")
            return {"power": True, "playing": resp.endswith("PL"), "paused": resp.endswith("PP")}
        except Exception:
            return {"power": False, "playing": False, "paused": False}
