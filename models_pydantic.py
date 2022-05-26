from pydantic import BaseModel
from typing import List, Optional


class Devices(BaseModel):
    devices: List[str] = []


class Volume(Devices):
    volume: int


class Experience(Devices):
    experience: str

class NewExperience(Devices):
    experience_name: Optional[str] = None
    apk_name: str
    command: str

class StartExperience(Devices):
    experience: str

