from fastapi import APIRouter, HTTPException
from app.schemas.fabric import FabricHemUpdate
from app.repositories import fabrics as repo
router = APIRouter()
@router.get("/fabrics")
def list_fabrics(): return {"items": repo.list_fabrics()}
@router.get("/fabrics/{fid}")
def get_fabric(fid: int):
    r = repo.get_fabric(fid)
    if not r: raise HTTPException(404)
    return r
@router.patch("/fabrics/{fid}/hems")
def update_hems(fid: int, body: FabricHemUpdate):
    r = repo.update_hems(fid, body.hem_top, body.hem_bottom)
    if not r: raise HTTPException(404)
    return r
