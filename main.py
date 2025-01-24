# main.py

import asyncio
import math
import time

from ble_lamp import MoonsideLamp
from theme import ThemeConfig, ThemeName
from color import RGBColor

async def demo():
    """
    Demonstrates using the MoonsideLamp class to:
      - Turn the lamp on
      - Set brightness
      - Apply a color
      - Apply a theme
      - Turn the lamp off
    """

    # Create a ThemeConfig for RAINBOW1, which allows 1 numeric param and 0 colors
    palette_config = ThemeConfig(
        name=ThemeName.BEAT2,
        colors=[RGBColor(255, 0, 0), RGBColor(0, 255, 0)]
    )

    # Example config for TWINKLE1, which has 2 color inputs and no numeric param
    twinkle_config = ThemeConfig(
        name=ThemeName.TWINKLE1,
        colors=[RGBColor(255, 0, 0), RGBColor(0, 0, 255)]
    )

    # lamp1 = MoonsideLamp("MOONSIDE-L1")
    lamp2 = MoonsideLamp("MOONSIDE-S1")

    base_color = RGBColor(138, 43, 226)
    duration = 30
    start_time = time.time()

    master_brightness = 0

    async with lamp2:
        await lamp2.turn_on()

        while start_time + duration > time.time():
            print(f"{master_brightness=}")
            master_brightness = max(0, min(1, master_brightness + 0.01))
            brightness_factor = math.sqrt(master_brightness)
            color_factor = math.sqrt(master_brightness)

            set_brightness = int(brightness_factor * 120)
            set_color = RGBColor(int(base_color.r * color_factor), int(base_color.g * color_factor), int(base_color.b * color_factor))
            await lamp2.set_color(set_color, brightness=set_brightness)
            await asyncio.sleep(0.05)

    # Replace "MOONSIDE-S1" with the actual BLE name broadcast by your lamp
    # async with lamp1, lamp2:
    #     print("Lamp connected.")
    #
    #     # Basic commands
    #     await lamp1.turn_on()
    #     await lamp2.turn_on()
    #     print("Lamp turned on.")

        # await lamp.set_brightness(80)
        # print("Lamp brightness set to 80.")
        #
        # # Set a bright green color
        # green = RGBColor(r=0, g=255, b=0)
        # await lamp.set_color(green, brightness=80)

        # Apply the RAINBOW1 theme
        # await lamp1.set_theme(palette_config)
        # print("Rainbow1 theme set.")

        # # Wait a bit, then switch to Twinkle1
        # await asyncio.sleep(3)
        # await lamp.set_theme(twinkle_config)
        # print("Twinkle1 theme set with red and blue colors.")
        #
        # # Finally, turn the lamp off
        # await asyncio.sleep(3)
        # await lamp.turn_off()
        # print("Lamp turned off.")

def main():
    asyncio.run(demo())

if __name__ == "__main__":
    main()
