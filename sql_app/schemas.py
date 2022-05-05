from typing import List, Optional

from fastapi import Form
from pydantic import BaseModel

from sql_app.models import DeviceTypes


class APKDetailsBase(BaseModel):
    apk_name: str
    command: Optional[str] = None
    device_type: DeviceTypes


class APKDetailsCreate(APKDetailsBase):
    pass


class APKDetails(APKDetailsBase):
    id: int

    class Config:
        orm_mode = True

