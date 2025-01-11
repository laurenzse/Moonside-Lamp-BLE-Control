# ble_lamp.py

import asyncio
from typing import Optional

from bleak import BleakScanner, BleakClient
from theme import ThemeConfig
from color import RGBColor


class MoonsideLamp:
    """
    Provides high-level controls for a Moonside lamp over BLE using Nordic UART Service (NUS).
    """

    NORDIC_UART_RX_DESCRIPTION = "Nordic UART RX"

    def __init__(
            self,
            device_name: str,
            max_reconnect_attempts: int = 3
    ) -> None:
        """
        :param device_name: The advertised BLE name of the lamp (e.g. "MOONSIDE-S1").
        :param max_reconnect_attempts: Number of times to try reconnecting if disconnected.
        """
        self.device_name: str = device_name
        self.max_reconnect_attempts: int = max_reconnect_attempts
        self.client: Optional[BleakClient] = None
        self.rx_characteristic = None

    async def __aenter__(self) -> "MoonsideLamp":
        """
        Allows usage like:
            async with MoonsideLamp("MOONSIDE-S1") as lamp:
                await lamp.turn_on()
        """
        await self._connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Ensures we disconnect from the BLE device upon exiting the context.
        """
        await self._disconnect()

    async def _connect(self) -> None:
        """
        Scan for the device and connect. Locate the RX characteristic.
        Raises an exception if not found or if characteristic is missing.
        """
        devices = await BleakScanner.discover()
        lamp_address = None

        for d in devices:
            if d.name == self.device_name:
                lamp_address = d.address
                break

        if lamp_address is None:
            raise RuntimeError(f"Device '{self.device_name}' not found during scan.")

        self.client = BleakClient(lamp_address)
        await self.client.connect()

        # Locate the RX characteristic
        for char in self.client.services.characteristics.values():
            if char.description == self.NORDIC_UART_RX_DESCRIPTION:
                self.rx_characteristic = char
                break

        if not self.rx_characteristic:
            raise RuntimeError(
                f"Unable to find characteristic '{self.NORDIC_UART_RX_DESCRIPTION}'."
            )

    async def _disconnect(self) -> None:
        """
        Disconnect from the BLE device if connected.
        """
        if self.client and self.client.is_connected:
            await self.client.disconnect()
        self.client = None

    async def _ensure_connected(self) -> None:
        """
        If the client is disconnected, try reconnecting up to 'max_reconnect_attempts'.
        Raises an exception if still unsuccessful.
        """
        if self.client and self.client.is_connected:
            return  # already connected, do nothing

        # Attempt reconnection
        attempts = 0
        while attempts < self.max_reconnect_attempts:
            try:
                await self._connect()
                return  # success
            except Exception:
                attempts += 1

        raise RuntimeError(
            f"Failed to reconnect to lamp '{self.device_name}' after "
            f"{self.max_reconnect_attempts} attempts."
        )

    async def _send_command(self, command: str) -> None:
        """
        Encode the command into ASCII bytes and send it to the lamp.
        Ensures the lamp is connected, optionally reconnecting if needed.
        """
        await self._ensure_connected()  # ensure we have a valid connection

        if not self.client or not self.client.is_connected:
            raise RuntimeError("Not connected to the lamp (after reconnection attempts).")

        data = bytes.fromhex(command.encode("ascii").hex())
        await self.client.write_gatt_char(self.rx_characteristic, data, response=True)

    # ----------------------------
    # Basic Lamp Control Methods
    # ----------------------------

    async def turn_on(self) -> None:
        """
        Turn the lamp on (reconnects if necessary).
        """
        await self._send_command("LEDON")

    async def turn_off(self) -> None:
        """
        Turn the lamp off (reconnects if necessary).
        """
        await self._send_command("LEDOFF")

    async def set_brightness(self, brightness: int) -> None:
        """
        Set the lamp brightness (0..120).
        Raises ValueError if out of range.
        """
        if not (0 <= brightness <= 120):
            raise ValueError("Brightness must be in the range 0..120.")

        cmd = f"BRIGH{brightness:03d}"
        await self._send_command(cmd)

    async def set_color(self, color: RGBColor, brightness: Optional[int] = None) -> None:
        """
        Set the lamp to an RGB color. Optionally specify brightness (0..120).
        Example: set_color(RGBColor(255, 0, 255), brightness=60).
        """
        cmd = f"COLOR{color.r:03d}{color.g:03d}{color.b:03d}"
        if brightness is not None:
            cmd += f" {brightness}"
        await self._send_command(cmd)

    # ---------------
    # Theme Methods
    # ---------------

    async def set_theme(self, theme_config: ThemeConfig) -> None:
        """
        Apply a theme using a validated ThemeConfig object.
        Example:
            theme_config = ThemeConfig(
                name=ThemeName.THEME1,
                colors=[RGBColor(255,0,0), RGBColor(0,0,255)]
            )
            await lamp.set_theme(theme_config)
        """
        cmd = theme_config.to_command_string()
        await self._send_command(cmd)

    # --------------------------------
    # Pixel-Level Control
    # --------------------------------

    async def set_pixel(self, pixel_id: int, brightness: int, color: RGBColor) -> None:
        """
        Set a single pixel's brightness and color using RGBColor.
        Example: "PIXEL,1,50 COLOR255000000" => pixel 1, brightness 50, color #FF0000

        :param pixel_id: index of the LED (0..N).
        :param brightness: pixel brightness (0..120).
        :param color: RGBColor for the pixel.
        """
        if not (0 <= brightness <= 120):
            raise ValueError("Pixel brightness must be in the range 0..120.")

        # Format color as "255000000", i.e., RRRGGGBBB with zero-padding
        color_str = f"{color.r:03d}{color.g:03d}{color.b:03d}"
        cmd = f"PIXEL,{pixel_id},{brightness} COLOR{color_str}"
        await self._send_command(cmd)

    async def apply_pixel_mode(self) -> None:
        """
        After setting pixels individually, call MODEPIXEL to apply the changes.
        """
        await self._send_command("MODEPIXEL")
