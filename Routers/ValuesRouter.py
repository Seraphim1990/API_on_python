# ValuesRouter.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import json

from DataBase.database import get_session
from DataBase.models import Values, Devices  # SQLAlchemy-модель
from DataBase.schemas import ValueCreate, ValueRead, ValueDelete, ValueUpdate
from Routers.crud import create_unit, get_all_units, get_one_unit, update_unit, delete_unit

values_router = APIRouter(prefix="/values", tags=["Values"])


# CREATE
@values_router.post("/create", response_model=ValueRead)
async def create_value(value: ValueCreate, session: AsyncSession = Depends(get_session)):
    return await create_unit(value, Values, session)


@values_router.get("/get_all", response_model=list[ValueRead])
async def get_all_values(session: AsyncSession = Depends(get_session)):
    return await get_all_units(Values, session)


@values_router.get("/get_logging_only", response_model=list[ValueRead])
async def get_logging_values(session: AsyncSession = Depends(get_session)):
    """
    Повертає тільки ті Values, де в settings є isLoging: true
    """
    result = await session.execute(select(Values))
    all_values = result.scalars().all()

    # Фільтруємо тільки ті, де isLoging = true
    logging_values = []
    for value in all_values:
        try:
            # settings це вже dict (SQLAlchemy автоматично парсить JSON)
            if value.settings and isinstance(value.settings, dict):
                if value.settings.get('isLoging') == True:
                    logging_values.append(value)
            # Якщо settings це string - парсимо вручну
            elif value.settings and isinstance(value.settings, str):
                settings_dict = json.loads(value.settings)
                if settings_dict.get('isLoging') == True:
                    logging_values.append(value)
        except Exception as e:
            print(f"Error parsing settings for value {value.id}: {e}")
            continue

    return logging_values


@values_router.get("/get_by_parent_id/{parent_id}", response_model=list[ValueRead])
async def get_by_parent_id(parent_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Values).where(Values.parentDeviceId == parent_id))
    values = result.scalars().all()
    if not values:
        device_result = await session.execute(select(Devices).where(Devices.id == parent_id))
        device_unit = device_result.scalar_one_or_none()
        if not device_unit:
            raise HTTPException(status_code=404, detail=f"Device with id {parent_id} not found")
        raise HTTPException(status_code=404, detail=f"No values found for device {device_unit.name}")
    return values


@values_router.put("/update/{val_id}", response_model=ValueRead)
async def update_value(val_id: int, val_update: ValueUpdate, session: AsyncSession = Depends(get_session)):
    try:
        return await update_unit(Values, val_id, val_update, session)
    except HTTPException:
        raise HTTPException(status_code=404, detail="Value not found")


# DELETE
@values_router.delete("/delete/{val_id}")
async def delete_value(val_id: int, session: AsyncSession = Depends(get_session)):
    try:
        return await delete_unit(Values, val_id, session)
    except HTTPException:
        raise HTTPException(status_code=404, detail="Value not found")