#DeviceRouter.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from DataBase.database import get_session
from DataBase.models import Devices, Nodes  # SQLAlchemy-модель
from DataBase.schemas import DeviceRead, DeviceCreate, DeviceUpdate
from Routers.crud import create_unit, get_all_units, get_one_unit, update_unit, delete_unit

devices_router = APIRouter(prefix="/devices", tags=["Devices"])

@devices_router.post("/create", response_model=DeviceRead)
async def create_devices(device: DeviceCreate, session: AsyncSession = Depends(get_session)):
    return await create_unit(device, Devices, session)


# READ ALL
@devices_router.get("/get_all", response_model=list[DeviceRead])
async def get_all_devices(session: AsyncSession = Depends(get_session)):
    return await get_all_units(Devices, session)

@devices_router.get("/get_by_parent_id/{parent_id}", response_model=list[DeviceRead])
async def get_devices_by_parent_id(parent_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Devices).where(Devices.parentNodeId == parent_id))
    devices = result.scalars().all()
    if not devices:
        node_result = await session.execute(select(Nodes).where(Nodes.id == parent_id))
        node_unit = node_result.scalar_one_or_none()
        if not node_unit:
            raise HTTPException(status_code=404, detail=f"Node with id {parent_id} not found")
        raise HTTPException(status_code=404, detail=f"No devices found for node {node_unit.ip}")
    return devices

@devices_router.get("/find_exists_addr_wit_parent_id", response_model=DeviceRead)
async def find_exists_addr_wit_parent_id(
        address: int,
        parent_id: int,
        session: AsyncSession = Depends(get_session)):

    result = await session.execute(select(Devices)
                                   .where(Devices.address == address)
                                   .where(Devices.parentNodeId == parent_id))
    devices = result.scalar_one_or_none()
    if not devices:
        raise HTTPException(status_code=404, detail="Device not found")
    return devices


# READ ONE
@devices_router.get("/get_device/{device_id}", response_model=DeviceRead)
async def get_device(device_id: int, session: AsyncSession = Depends(get_session)):
    try:
        return await get_one_unit(Devices, device_id, session)
    except HTTPException :
        raise HTTPException(status_code=404, detail="Device not found")

# UPDATE
@devices_router.put("/update/{device_id}", response_model=DeviceRead)
async def update_node(device_id: int, device_update: DeviceUpdate, session: AsyncSession = Depends(get_session)):
    try:
        return await update_unit(Devices, device_id, device_update, session)
    except HTTPException:
        raise HTTPException(status_code=404, detail="Device not found")

# DELETE
@devices_router.delete("/delete/{device_id}")
async def delete_node(device_id: int, session: AsyncSession = Depends(get_session)):
    try:
        return await delete_unit(Devices, device_id, session)
    except HTTPException:
        raise HTTPException(status_code=404, detail="Device not found")

