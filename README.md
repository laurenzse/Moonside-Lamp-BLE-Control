# Moonside Lamp BLE Control

This project provides a **Python-based** Bluetooth Low Energy (BLE) control interface for the **Moonside Smart Lamp**. It uses the [Bleak](https://github.com/hbldh/bleak) library to communicate with the lamp via its Nordic UART Service (NUS). It allows you to:

- Turn the lamp **on** and **off**  
- Set the **brightness**  
- Set a **color** (using RGB values)  
- Apply **thematic** color/effect configurations  
- Optionally manipulate **individual pixels** (if supported by your lamp)

---

## Table of Contents


1. [Installation](#installation)  
2. [Usage](#usage)  
3. [API Overview](#api-overview)  
   - [MoonsideLamp Class](#moonsidelamp-class)  
   - [RGBColor](#rgbcolor)  
   - [ThemeConfig and ThemeName](#themeconfig-and-themename)  
4. [Available Themes](#available-themes)  
5. [Example Code Snippets](#example-code-snippets)  
6. [License](#license)  

---


---

## Installation

1. **Clone** or **download** this repository:

   ```bash
   git clone https://github.com/<your-repo>/my_moonside_project.git
   cd my_moonside_project
   ```

2. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

   This will install [Bleak](https://github.com/hbldh/bleak) and any other required libraries.

3. **Confirm BLE Support**:

   - On **Windows**, ensure you have at least Windows 10 with Bluetooth LE support.  
   - On **Linux**, you may need additional packages such as `bluez` and permission adjustments to use BLE.  
   - On **macOS**, recent versions support BLE by default, but you must allow the Terminal (or Python) to access Bluetooth in System Preferences.

---

## Usage

1. **Power on** your Moonside Lamp, ensuring **Bluetooth** is active.
2. **Find** or **know** the lamp’s BLE **name** (often `MOONSIDE-S1` or similar).
3. **Run** your Python script (e.g., `main.py`) that uses `MoonsideLamp`.

Example:

```bash
python main.py
```

- The script will **scan** for BLE devices.
- If a device matching your lamp’s **advertised name** is found, it will **connect** and **send** commands.

*(See [Example Code Snippets](#example-code-snippets) below for more detailed usage.)*

---

## API Overview

### MoonsideLamp Class

Found in **`ble_lamp.py`**, this class is used to **connect** to and **control** the lamp. It supports Python’s **async context manager** syntax:

```python
async with MoonsideLamp("MOONSIDE-S1") as lamp:
    await lamp.turn_on()
    await lamp.set_brightness(80)
    await lamp.turn_off()
```

#### Key Methods

- **`turn_on()`**: Turns the lamp **ON**.  
- **`turn_off()`**: Turns the lamp **OFF**.  
- **`set_brightness(brightness: int)`**: Sets the lamp brightness (0–120).  
- **`set_color(color: RGBColor, brightness: Optional[int] = None)`**: Sets the lamp color using an `RGBColor`; optionally override brightness.  
- **`set_theme(theme_config: ThemeConfig)`**: Applies a theme by sending a validated command string.  
- **`set_pixel(pixel_id: int, brightness: int, color: RGBColor)`**: Sets a single pixel to a color (advanced usage).  
- **`apply_pixel_mode()`**: Applies all pixel changes.

### RGBColor

Found in **`color.py`**, this dataclass models a basic **RGB** color:

```python
@dataclass
class RGBColor:
    r: int  # (0..255)
    g: int  # (0..255)
    b: int  # (0..255)

    # ...
```

Use it like:

```python
color = RGBColor(r=255, g=0, b=255)  # Purple
```

### ThemeConfig and ThemeName

Defined in **`theme.py`**:

1. **`ThemeName`**: An `Enum` listing **all supported themes** (like `THEME1`, `THEME2`, etc.).  
2. **`THEME_METADATA`**: A dictionary mapping each `ThemeName` to:
   - `num_colors`: How many color values the theme expects  
   - `has_numeric`: Whether the theme expects a single numeric parameter (currently disabled for all themes, because the exact usage is unknown)
3. **`ThemeConfig`**: A dataclass that:
   - Holds a `name: ThemeName`  
   - Optionally a `numeric_param: int` (if `has_numeric=True`)  
   - A list of `colors: List[RGBColor]`  
   - Validates that the **correct** number of colors and numeric parameters are provided

Example usage:

```python
from theme import ThemeConfig, ThemeName
from color import RGBColor

# Create a configuration for THEME1, which requires 2 colors, no numeric param
config = ThemeConfig(
    name=ThemeName.THEME1,
    colors=[RGBColor(255,0,0), RGBColor(0,0,255)]
)
```

Then pass it to the lamp:

```python
await lamp.set_theme(config)
```

---

## Available Themes

Below is the current list of **ThemeName** entries and the number of color inputs each requires (based on `THEME_METADATA`). All of these do **not** accept a numeric parameter unless indicated otherwise (`has_numeric=False` in all entries shown):

Here is the simplified table of the themes, focusing only on their names and the number of colors they require:

| **Theme Name**    | **num_colors** |
|-------------------|----------------|
| `THEME1`          | 2              |
| `THEME2`          | 2              |
| `THEME3`          | 6              |
| `THEME4`          | 2              |
| `THEME5`          | 2              |
| `GRADIENT1`       | 2              |
| `GRADIENT2`       | 3              |
| `PULSING1`        | 2              |
| `TWINKLE1`        | 2              |
| `WAVE1`           | 2              |
| `BEAT1`           | 3              |
| `BEAT2`           | 2              |
| `BEAT3`           | 3              |
| `COLORDROP1`      | 2              |
| `LAVA1`           | 2              |
| `FIRE2`           | 4              |
| `PALETTE2`        | 6              |


---

## Example Code Snippets

### 1. Basic Control

```python
import asyncio
from ble_lamp import MoonsideLamp
from color import RGBColor

async def basic_control_demo():
    async with MoonsideLamp("MOONSIDE-S1") as lamp:
        # Turn on
        await lamp.turn_on()
        
        # Set brightness to 100
        await lamp.set_brightness(100)
        
        # Set color to green with brightness 80
        green = RGBColor(r=0, g=255, b=0)
        await lamp.set_color(green, brightness=80)

        # Turn off after a delay
        await asyncio.sleep(2)
        await lamp.turn_off()

if __name__ == "__main__":
    asyncio.run(basic_control_demo())
```

### 2. Using a Theme

```python
import asyncio
from ble_lamp import MoonsideLamp
from theme import ThemeConfig, ThemeName
from color import RGBColor

async def theme_demo():
    async with MoonsideLamp("MOONSIDE-S1") as lamp:
        # THEME1 requires 2 colors
        theme_config = ThemeConfig(
            name=ThemeName.THEME1,
            colors=[RGBColor(255, 0, 0), RGBColor(0, 0, 255)]
        )
        await lamp.set_theme(theme_config)

        await asyncio.sleep(5)

        # Switch to THEME3, which requires 6 colors
        theme_config = ThemeConfig(
            name=ThemeName.THEME3,
            colors=[
                RGBColor(255, 0, 0),
                RGBColor(0, 255, 0),
                RGBColor(0, 0, 255),
                RGBColor(255, 255, 0),
                RGBColor(0, 255, 255),
                RGBColor(255, 0, 255),
            ]
        )
        await lamp.set_theme(theme_config)

        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(theme_demo())
```

### 3. Pixel-Level Commands

*(Advanced / optional — only if your Moonside Lamp firmware supports direct pixel addressing.)*

```python
async def pixel_demo():
    async with MoonsideLamp("MOONSIDE-S1") as lamp:
        # Turn on the lamp
        await lamp.turn_on()
        
        # Set pixel #1 to brightness 50, color green
        green = RGBColor(r=0, g=255, b=0)
        await lamp.set_pixel(pixel_id=1, brightness=50, color_str="255000000")
        
        # Apply changes
        await lamp.apply_pixel_mode()
```

---

## License

This project is provided as-is and is **unofficial**. The underlying Bluetooth protocol for the Moonside Lamp was partially reverse-engineered. Use it at your own risk and be mindful of any firmware updates from the official vendor that could change or break compatibility.  

You may adapt or distribute this code under your own chosen license (e.g., MIT, Apache 2.0) if appropriate. Remember to respect any **trademarks** or **intellectual property** of the Moonside brand.