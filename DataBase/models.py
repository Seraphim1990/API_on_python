#models.py
from sqlalchemy import Integer, String, Boolean, ForeignKey, Double, BigInteger, Index, JSON
from sqlalchemy.dialects.mysql import BIGINT, DOUBLE
from sqlalchemy.orm import Mapped, mapped_column
from DataBase.database import Base

class Nodes(Base):
    __tablename__ = "nodes"

    id: Mapped[int] = mapped_column(Integer, primary_key= True, autoincrement= True, nullable= False)
    description: Mapped[str] = mapped_column(String)
    ip: Mapped[str] = mapped_column(String(100), nullable= False)
    port: Mapped[int] = mapped_column(Integer, nullable= False)

class Devices(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key= True, autoincrement= True, nullable= False)
    description: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String(100), nullable= False)
    address: Mapped[int] = mapped_column(Integer, nullable= False)
    parentNodeId: Mapped[int] = mapped_column(Integer,
                                              ForeignKey("nodes.id", ondelete= "CASCADE", onupdate= "CASCADE"),
                                              nullable= False)
    timeForRecall: Mapped[int] = mapped_column(Integer, nullable= False)
    timeForRetry: Mapped[int] = mapped_column(Integer, nullable= False)
    retryCount: Mapped[int] = mapped_column(Integer, nullable= False)
    timeForResponce: Mapped[int] = mapped_column(Integer, nullable= False)
    isActive: Mapped[bool] = mapped_column(Boolean, default=True)
    readByGroup: Mapped[bool] = mapped_column(Boolean, default=True)

class Values(Base):
    __tablename__ = "value_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    parentDeviceId: Mapped[int] = mapped_column(Integer, ForeignKey("devices.id",
                                                                    ondelete="CASCADE", onupdate="CASCADE"))
    decodingTypeId: Mapped[int] = mapped_column(Integer, ForeignKey("decodingtype.id", ondelete="RESTRICT", onupdate="CASCADE"))
    settings: Mapped[str] = mapped_column(JSON, nullable=True)
    tag: Mapped[str] = mapped_column(String(255), nullable=True)

class DecodingType(Base):
    __tablename__ = "decodingtype"

    id: Mapped[int] = mapped_column(Integer, primary_key= True, nullable= False, autoincrement= True)
    uiName: Mapped[str] = mapped_column(String(100), nullable= False)
    programName: Mapped[str] = mapped_column(String, nullable= False)

class QmlDecodingAddons(Base):
    __tablename__ = "qmldecodingaddons"

    id: Mapped[int] = mapped_column(Integer, primary_key= True, autoincrement= True)
    parentDescriptionType: Mapped[int] = mapped_column(Integer, ForeignKey("decodingtype.id"), nullable= False)
    textForQML: Mapped[str] = mapped_column(String)

class Measures(Base):
    __tablename__ = "measures"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True, nullable=False)
    valueId: Mapped[int] = mapped_column(Integer, ForeignKey("value_items.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    measureValue: Mapped[float] = mapped_column(DOUBLE, nullable=False)
    measureTime: Mapped[int] = mapped_column(BIGINT, nullable=False)