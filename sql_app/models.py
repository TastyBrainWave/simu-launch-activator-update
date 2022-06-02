import enum

from sqlalchemy import Column, Integer, String
from sqlalchemy_utils import ChoiceType

from .database import Base


class DeviceTypes(enum.IntEnum):
    android = 0
    quest = 1
    retrieved_from_system = 2


class APKDetails(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    experience_name = Column(String, index=True)
    apk_name = Column(String, index=True)
    command = Column(String, index=True)
    device_type = Column(ChoiceType(DeviceTypes, impl=Integer()))


class DeviceInfo(Base):
    __tablename__ = 'devices'
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True)
    col = Column(String)
    icon = Column(String)


class Settings(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True, index=True)
    screen_updates = Column(Integer, index=True, default=8)
