import asyncio
import pytweening
from ble_lamp import MoonsideLamp
from color import RGBColor
from theme import ThemeConfig, ThemeName

async def animate_theme(lamp: MoonsideLamp, duration: float, start_colors: list, end_colors: list, start_brightness: int, end_brightness: int, color_tweening_effect=pytweening.easeInOutQuad, brightness_tweening_effect=pytweening.easeInOutQuad):
    """
    Gradually animates a theme by changing its colors and brightness over time.

    Args:
        lamp (MoonsideLamp): An instance of the MoonsideLamp class.
        duration (float): The duration of the animation in seconds.
        start_colors (list): A list of RGBColor objects for the starting colors.
        end_colors (list): A list of RGBColor objects for the ending colors.
        start_brightness (int): The starting brightness level (0-120).
        end_brightness (int): The ending brightness level (0-120).
        color_tweening_effect (callable): A tweening function for colors (default is easeInOutQuad).
        brightness_tweening_effect (callable): A tweening function for brightness (default is easeInOutQuad).

    Returns:
        None
    """
    # Ensure start and end colors have the same length
    if len(start_colors) != len(end_colors):
        raise ValueError("Start and end color lists must have the same length.")

    # Define minimum wait time
    color_min_wait = 60 * 2.5  # Minimum wait time in seconds
    brightness_min_wait = 10  # Minimum wait time in seconds
    start_time = asyncio.get_event_loop().time()  # Record the overall start time

    while True:
        # Calculate elapsed time
        elapsed_time = asyncio.get_event_loop().time() - start_time

        # Calculate progress (0 to 1)
        progress = min(elapsed_time / duration, 1.0)

        # Interpolate colors using the color tweening function
        current_colors = [
            RGBColor(
                r=int(color_tweening_effect(progress) * (end.r - start.r) + start.r),
                g=int(color_tweening_effect(progress) * (end.g - start.g) + start.g),
                b=int(color_tweening_effect(progress) * (end.b - start.b) + start.b),
            )
            for start, end in zip(start_colors, end_colors)
        ]

        # Interpolate brightness using the brightness tweening function
        current_brightness = int(brightness_tweening_effect(progress) * (end_brightness - start_brightness) + start_brightness)

        # Set the theme with the interpolated colors
        theme_config = ThemeConfig(name=ThemeName.GRADIENT1, colors=current_colors)
        command_start_time = asyncio.get_event_loop().time()
        await lamp.set_theme(theme_config)

        # Calculate elapsed time for the command
        command_elapsed_time = asyncio.get_event_loop().time() - command_start_time

        # Wait for the remaining time to fill up the min_wait time if necessary
        wait_time = max(0, brightness_min_wait - command_elapsed_time)
        if wait_time > 0:
            await asyncio.sleep(wait_time)

        # Set the brightness
        await lamp.set_brightness(current_brightness)

        # Break the loop if the animation is complete
        if progress >= 1.0:
            break

        # Calculate elapsed time for the command
        command_elapsed_time = asyncio.get_event_loop().time() - command_start_time

        # Wait for the remaining time to fill up the min_wait time if necessary
        wait_time = max(0, color_min_wait - command_elapsed_time)
        if wait_time > 0:
            await asyncio.sleep(wait_time)

# Example usage
if __name__ == "__main__":
    async def main():
        async with MoonsideLamp("MOONSIDE-L1") as lamp:
            # Animate theme colors and brightness
            start_colors = [RGBColor(0, 0, 255), RGBColor(0, 255, 0)]  # Blue and Green
            end_colors = [RGBColor(255, 165, 0), RGBColor(128, 0, 128)]  # Orange and Purple
            await animate_theme(
                lamp,
                duration=60.0*30,
                start_colors=start_colors,
                end_colors=end_colors,
                start_brightness=20,
                end_brightness=120,
                color_tweening_effect=pytweening.easeInQuad,
                brightness_tweening_effect=pytweening.easeOutQuad
            )

    asyncio.run(main())
