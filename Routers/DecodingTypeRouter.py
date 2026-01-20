#DecodingTypeRouter.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from DataBase.database import get_session
from DataBase.models import DecodingType, QmlDecodingAddons  # SQLAlchemy-модель
from DataBase.schemas import QmlDecodingAddonsGet, DecidingTypeGet
from Routers.crud import get_all_units

decoding_type_router = APIRouter(prefix="/decoding_type", tags=["RegisterDecoding"])

@decoding_type_router.get("/get_all", response_model=list[DecidingTypeGet])
async def get_all_decoders(session: AsyncSession = Depends(get_session)):
    return await get_all_units(DecodingType, session)

@decoding_type_router.get("/get_addons/{id_decoding_type}", response_model= QmlDecodingAddonsGet)
async def get_qml_addon(id_decoding_type: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(QmlDecodingAddons).where(QmlDecodingAddons.parentDescriptionType == id_decoding_type))
    addon = result.scalar_one_or_none()
    if not addon:
        decoding_result = await session.execute(select(DecodingType).where(DecodingType.id == id_decoding_type))
        decoding_unit = decoding_result.scalar_one_or_none()
        if not decoding_unit:
            raise HTTPException(status_code=404, detail=f"Decoding type with id {id_decoding_type} not found")
        raise HTTPException(status_code=404, detail=f"No addons found for decoding type {decoding_unit.uiName}")
    return addon