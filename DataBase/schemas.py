# schemas.py
from pydantic import BaseModel


class NodeBase(BaseModel):
    description: str | None = None
    ip: str
    port: int


class NodeCreate(NodeBase):
    pass


class NodeRead(NodeBase):
    id: int

    class Config:
        orm_mode = True


class NodeUpdate(BaseModel):
    id: int | None = None
    description: str | None = None
    ip: str | None = None
    port: int | None = None

    class Config:
        orm_mode = True


class NodeDelete(BaseModel):
    id: int


class DeviceBase(BaseModel):
    description: str | None = None
    name: str
    address: int
    parentNodeId: int
    timeForRecall: int
    timeForRetry: int
    retryCount: int
    timeForResponce: int
    isActive: bool
    readByGroup: bool


class DeviceCreate(DeviceBase):
    pass


class DeviceRead(DeviceBase):
    id: int

    class Config:
        orm_mode = True


class DeviceUpdate(BaseModel):
    # id: int
    description: str | None = None
    name: str | None = None
    address: int | None = None
    parentNodeId: int | None = None
    timeForRecall: int | None = None
    timeForRetry: int | None = None
    retryCount: int | None = None
    timeForResponce: int | None = None
    isActive: bool | None = None
    readByGroup: bool | None = None

    class Config:
        orm_mode = True


class DeviceDelete(BaseModel):
    id: int


class ValuesBase(BaseModel):
    name: str
    parentDeviceId: int
    decodingTypeId: int
    tag: str | None = None
    settings: dict


class ValueCreate(ValuesBase):
    pass


class ValueRead(ValuesBase):
    id: int

    class Config:
        orm_mode = True


class ValueUpdate(ValuesBase):
    name: str | None = None
    parentDeviceId: int | None = None
    decodingTypeId: int | None = None
    tag: str | None = None
    settings: dict | None = None

    class Config:
        orm_mode = True


class ValueDelete(BaseModel):
    id: int


class DecidingTypeGet(BaseModel):
    id: int
    uiName: str
    programName: str


class QmlDecodingAddonsGet(BaseModel):
    id: int
    parentDescriptionType: int
    textForQML: str

    class Config:
        orm_mode = True


class ActualData(BaseModel):
    tag: str
    timestamp: int
    value: float


class EventUpdate(BaseModel):
    update: dict[str, dict[int, float]]


class EventGet(BaseModel):
    get: list[str]


# Нові схеми для Measures
class MeasureBase(BaseModel):
    valueId: int
    measureValue: float
    measureTime: int


class MeasureCreate(BaseModel):
    valueId: int
    measureValue: float
    measureTime: int | None = None  # Може бути None, якщо використовується DEFAULT в БД

    class Config:
        orm_mode = True


class MeasureRead(MeasureBase):
    id: int

    class Config:
        orm_mode = True


class MeasureUpdate(BaseModel):
    valueId: int | None = None
    measureValue: float | None = None
    measureTime: int | None = None

    class Config:
        orm_mode = True


class MeasureDelete(BaseModel):
    id: int