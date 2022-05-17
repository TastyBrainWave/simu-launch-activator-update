from pydantic import BaseModel
from typing import List


class Devices(BaseModel):
    devices: List[str] = []


class Volume(Devices):
    volume: int


class Experience(Devices):
    experience: str

class NewExperience(Devices):
    apk_name: str
    command: str

