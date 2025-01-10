from dataclasses import dataclass

@dataclass
class RGBColor:
    """
    Represents an RGB color. Each channel is an integer from 0 to 255.
    """
    r: int
    g: int
    b: int

    def to_commastr(self) -> str:
        """
        Convert the color to a string in the format: "R,G,B,".
        Example: RGBColor(255, 0, 255) → "255,0,255,"
        """
        return f"{self.r},{self.g},{self.b},"
