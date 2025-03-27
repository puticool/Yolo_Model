from fastapi import APIRouter;

router = APIRouter()

@router.get("/", tags=["hello"])
async def read_root():
    return {"message": "Chào mừng đến với YOLO WebSocket API"}