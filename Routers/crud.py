#crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException

async def create_unit(pydentic_model, orm_model, session: AsyncSession):
    new_unit = orm_model(**pydentic_model.dict())
    session.add(new_unit)
    await session.commit()
    await session.refresh(new_unit)
    return new_unit

async def get_all_units(orm_model, session: AsyncSession):
    result = await session.execute(select(orm_model))
    return result.scalars().all()

async def get_one_unit(orm_model, id_unit, session: AsyncSession):
    result = await session.execute(select(orm_model).where(orm_model.id == id_unit))
    unit = result.scalar_one_or_none()
    if not unit:
        raise HTTPException
    return unit

async def update_unit(orm_model, unit_id, new_unit_data, session: AsyncSession):
    result = await session.execute(select(orm_model).where(orm_model.id == unit_id))
    unit = result.scalar_one_or_none()
    if not unit:
        raise HTTPException

    for field, value in new_unit_data.dict(exclude_unset=True).items():
        setattr(unit, field, value)

    await session.commit()
    await session.refresh(unit)
    return unit

async def delete_unit(orm_model, unit_id, session: AsyncSession):
    result = await session.execute(select(orm_model).where(orm_model.id == unit_id))
    unit = result.scalar_one_or_none()
    if not unit:
        raise HTTPException(status_code=404)
    await session.delete(unit)
    await session.commit()
    return {"ok": True}