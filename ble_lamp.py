import asyncio
from typing import Optional

from bleak import BleakScanner, BleakClient
from theme import ThemeConfig
from color import RGBColor


class MoonsideLamp:
    """
    Provides high-level controls for a Moonside lamp over BLE using Nordic UART Service (NUS).
    """

    NORDIC_UART_RX_DESCRIPTION = (
        "Nordic UART RX"  # Commonly used to find the TX->RX characteristic
    )

    def __init__(self, device_name: str) -> None:
        """
        Initialize the MoonsideLamp instance with the given BLE name.
        :param device_name: The advertised BLE name of the lamp, e.g. "MOONSIDE-S1".
        """
        self.device_name: str = device_name
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
        Ensures disconnection from the BLE device upon exiting the context.
        """
        await self._disconnect()

    async def _connect(self) -> None:
        """
        Finds the device by scanning and connects to it. Locates the RX characteristic.
        Raises an exception if the lamp is not found or if the characteristic is missing.
        """
        # Discover devices
        devices = await BleakScanner.discover()
        lamp_address = None

        # Find device by name
        for d in devices:
            if d.name == self.device_name:
                lamp_address = d.address
                break

        if lamp_address is None:
            raise RuntimeError(f"Device '{self.device_name}' not found during scan.")

        # Create a BLE client and connect
        self.client = BleakClient(lamp_address)
        await self.client.connect()

        # Locate the RX characteristic by its description or use a known UUID
        for index, char in self.client.services.characteristics.items():
            if char.description == self.NORDIC_UART_RX_DESCRIPTION:
                self.rx_characteristic = char
                break

        if not self.rx_characteristic:
            raise RuntimeError(
                f"Unable to find characteristic '{self.NORDIC_UART_RX_DESCRIPTION}'."
            )

    async def _disconnect(self) -> None:
        """
        Disconnect from the BLE device if currently connected.
        """
        if self.client and self.client.is_connected:
            await self.client.disconnect()
        self.client = None

    async def _send_command(self, command: str) -> None:
        """
        Encode the ASCII command into bytes and send it to the lamp.
        :param command: The command string (e.g. "LEDOFF", "THEME.RAINBOW1.20,")
        """
        if not self.client or not self.client.is_connected:
            raise RuntimeError("Not connected to the lamp.")

        data = bytes.fromhex(command.encode("ascii").hex())
        await self.client.write_gatt_char(self.rx_characteristic, data, response=True)

    # ----------------------------
    # Basic Lamp Control Methods
    # ----------------------------

    async def turn_on(self) -> None:
        """
        Turn the lamp on.
        """
        await self._send_command("LEDON")

    async def turn_off(self) -> None:
        """
        Turn the lamp off.
        """
        await self._send_command("LEDOFF")

    async def set_brightness(self, brightness: int) -> None:
        """
        Set the lamp brightness. Range is typically 0..120 as discovered.
        :param brightness: The brightness level to set (0..120).
        """
        if not (0 <= brightness <= 120):
            raise ValueError("Brightness must be in the range 0..120.")
        cmd = f"BRIGH{brightness:03d}"
        await self._send_command(cmd)

    async def set_color(
        self, color: RGBColor, brightness: Optional[int] = None
    ) -> None:
        """
        Set the lamp color using an RGBColor object. Optionally specify brightness (0..120).

        :param color: An RGBColor specifying red, green, and blue channels (0..255).
        :param brightness: Optional brightness override (0..120).
        """
        # Example final command: "COLOR255000255 60"
        # If brightness is omitted, then "COLOR255000255"
        cmd = f"COLOR{color.r:03d}{color.g:03d}{color.b:03d}"
        if brightness is not None:
            cmd += f" {brightness}"
        await self._send_command(cmd)

    # ---------------
    # Theme Methods
    # ---------------

    async def set_theme(self, theme_config: ThemeConfig) -> None:
        """
        Apply a theme to the lamp using a validated ThemeConfig object.
        :param theme_config: The ThemeConfig specifying the theme name, numeric param, and colors.
        """
        cmd = theme_config.to_command_string()
        await self._send_command(cmd)

    # --------------------------------
    # Pixel-Level Control (Optional)
    # --------------------------------

    async def set_pixel(self, pixel_id: int, brightness: int, color: RGBColor) -> None:
        """
        Set a single pixel's brightness and color.
        Example command: "PIXEL,1,50 COLOR255000000" → pixel 1, brightness 50, color #FF0000
        :param pixel_id: The index of the LED (0..N).
        :param brightness: Brightness for this pixel (0..120).
        :param color: An RGBColor specifying red, green, and blue channels (0..255).
        """
        cmd = f"PIXEL,{pixel_id},{brightness} COLOR{color.r:03d}{color.g:03d}{color.b:03d}"
        await self._send_command(cmd)

    async def apply_pixel_mode(self) -> None:
        """
        After setting pixels individually, call MODEPIXEL to apply the changes.
        """
        await self._send_command("MODEPIXEL")
