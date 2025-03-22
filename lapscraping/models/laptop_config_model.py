from pydantic.dataclasses import dataclass
from typing import Optional


@dataclass
class LaptopConfigModel:
    screen_spec: Optional[str]
    cpu: str
    ram: str
    hdd: str
    os: Optional[str]
    graphics_card: Optional[str]
    keyboard_layout: Optional[str]
    