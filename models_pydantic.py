from pydantic import BaseModel


class Devices(BaseModel):
    devices: list[str] = []


class Volume(Devices):
    volume: int


class Experience(Devices):
    experience: str
