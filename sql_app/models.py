from sqlalchemy import Column, Integer, String
from sqlalchemy_utils import ChoiceType

from .database import Base

import enum
class DeviceTypes(enum.IntEnum):
    android = 0
    quest = 1

class APKDetails(Base):

    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    apk_name = Column(String, index=True)
    command = Column(String, index=True)
    device_type = Column(ChoiceType(DeviceTypes, impl=Integer()))
