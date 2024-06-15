from fastapi import APIRouter, status #เพื่อใช้ในการสร้างเส้นทางของ API

router = APIRouter() #สร้าง instance ของ APIRouter เพื่อนำไปใช้ในการกำหนดเส้นทางของ API

@router.get("/", status_code=status.HTTP_200_OK)
async def read_bigc():
    return {"message": "This is the big c endpoint"}