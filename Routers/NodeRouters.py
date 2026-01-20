#NodeRouters.py
from xml.sax.saxutils import escape

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from DataBase.database import get_session
from DataBase.models import Nodes# SQLAlchemy-модель
from DataBase.schemas import NodeCreate, NodeRead, NodeUpdate
from Routers.crud import create_unit, get_all_units, get_one_unit, update_unit, delete_unit

nodes_router = APIRouter(prefix="/nodes", tags=["Nodes"])


# CREATE
@nodes_router.post("/create", response_model=NodeRead)
async def create_node(node: NodeCreate, session: AsyncSession = Depends(get_session)):
    return await create_unit(node, Nodes, session)


# READ ALL
@nodes_router.get("/get_all", response_model=list[NodeRead])
async def get_all_nodes(session: AsyncSession = Depends(get_session)):
    return await get_all_units(Nodes, session)


# READ ONE
@nodes_router.get("/by_id/{node_id}", response_model=NodeRead)
async def get_node_dy_id(node_id: int, session: AsyncSession = Depends(get_session)):
    try:
        return await get_one_unit(Nodes, node_id, session)
    except HTTPException :
        raise HTTPException(status_code=404, detail="Node not found")

@nodes_router.get("/by_ip/{ip_node}", response_model=NodeRead)
async def get_node_by_ip(ip_node: str,
                         session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Nodes).where(Nodes.ip == ip_node))
    unit = result.scalar_one_or_none()
    if not unit:
        raise HTTPException(status_code=404, detail="Node not found")
    return unit

# UPDATE
@nodes_router.put("/update/{node_id}", response_model=NodeRead)
async def update_node(node_id: int, node_update: NodeUpdate, session: AsyncSession = Depends(get_session)):
    try:
        return await update_unit(Nodes, node_id, node_update, session)
    except HTTPException:
        raise HTTPException(status_code=404, detail="Node not found")

# DELETE
@nodes_router.delete("/delete/{node_id}")
async def delete_node(node_id: int, session: AsyncSession = Depends(get_session)):
    try:
        return await delete_unit(Nodes, node_id, session)
    except HTTPException:
        raise HTTPException(status_code=404, detail="Node not found")

