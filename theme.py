from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional
from color import RGBColor

class ThemeName(Enum):
    """
    Enumerates all known theme identifiers for the Moonside lamp.
    The enum value is the exact string expected by the lamp's firmware.
    """
    THEME1 = "THEME1"
    THEME2 = "THEME2"
    THEME4 = "THEME4"
    THEME5 = "THEME5"
    GRADIENT1 = "GRADIENT1"
    PULSING1 = "PULSING1"
    TWINKLE1 = "TWINKLE1"
    WAVE1 = "WAVE1"
    BEAT2 = "BEAT2"
    COLORDROP1 = "COLORDROP1"
    GRADIENT2 = "GRADIENT2"
    LAVA1 = "LAVA1"
    BEAT1 = "BEAT1"
    BEAT3 = "BEAT3"
    FIRE2 = "FIRE2"
    PALETTE2 = "PALETTE2"
    THEME3 = "THEME3"

# Each theme can have a fixed number of colors (0..N)
# and at most one numeric parameter (speed, intensity, etc.).
THEME_METADATA = {
    ThemeName.PALETTE2:   {"num_colors": 6, "has_numeric": False},
    ThemeName.FIRE2:      {"num_colors": 4, "has_numeric": False},
    ThemeName.THEME1:     {"num_colors": 2, "has_numeric": False},
    ThemeName.THEME2:     {"num_colors": 2, "has_numeric": False},
    ThemeName.THEME3:     {"num_colors": 6, "has_numeric": False},
    ThemeName.THEME4:     {"num_colors": 2, "has_numeric": False},
    ThemeName.THEME5:     {"num_colors": 2, "has_numeric": False},
    ThemeName.WAVE1:      {"num_colors": 2, "has_numeric": False},
    ThemeName.BEAT1:      {"num_colors": 3, "has_numeric": False},
    ThemeName.BEAT2:      {"num_colors": 2, "has_numeric": False},
    ThemeName.BEAT3:      {"num_colors": 3, "has_numeric": False},
    ThemeName.GRADIENT1:  {"num_colors": 2, "has_numeric": False},
    ThemeName.GRADIENT2:  {"num_colors": 3, "has_numeric": False},
    ThemeName.TWINKLE1:   {"num_colors": 2, "has_numeric": False},
    ThemeName.COLORDROP1: {"num_colors": 2, "has_numeric": False},
    ThemeName.LAVA1:      {"num_colors": 2, "has_numeric": False},
    ThemeName.PULSING1:   {"num_colors": 2, "has_numeric": False},
}


@dataclass
class ThemeConfig:
    """
    Represents a configuration for a specific theme. This includes:
    - Which theme (e.g. RAINBOW1, TWINKLE1, etc.)
    - A single optional numeric parameter (e.g. speed or intensity)
    - A specific number of colors, depending on the theme
    """
    name: ThemeName
    numeric_param: Optional[int] = None
    colors: List[RGBColor] = field(default_factory=list)

    def validate(self) -> None:
        """
        Validate that the number of colors and presence/absence of a numeric parameter
        match the theme's specification in THEME_METADATA.
        """
        meta = THEME_METADATA[self.name]

        # Check color count
        required_colors = meta["num_colors"]
        if len(self.colors) != required_colors:
            raise ValueError(
                f"Theme {self.name.value} requires {required_colors} color(s), "
                f"but got {len(self.colors)}."
            )

        # Check numeric parameter
        has_numeric = meta["has_numeric"]
        if has_numeric and self.numeric_param is None:
            raise ValueError(f"{self.name.value} requires 1 numeric parameter.")
        if not has_numeric and self.numeric_param is not None:
            raise ValueError(f"{self.name.value} does not accept a numeric parameter.")

    def to_command_string(self) -> str:
        """
        Build the final ASCII command string for the lamp.
        For example:
          - THEME.RAINBOW1.20,
          - THEME.TWINKLE1.255,0,0,0,0,255,
        """
        self.validate()

        # Command format: "THEME.<theme>.PARAMS,"
        # Where PARAMS can be:
        #   - optional numeric param (if has_numeric)
        #   - color sequences in the format "R,G,B,"
        cmd_prefix = f"THEME.{self.name.value}."
        parts = []

        # If a numeric parameter is present, add it first
        if self.numeric_param is not None:
            parts.append(str(self.numeric_param))

        # Then each color in "R,G,B," format
        for c in self.colors:
            parts.append(c.to_commastr())

        # Join them
        param_str = "".join(parts)
        if not param_str.endswith(","):
            param_str += ","

        return cmd_prefix + param_str
