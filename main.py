from typing import Union
from fastapi import FastAPI, status
from routers.index import router as index_router #นำเข้าเส้นทางจากไฟล์ routers.index
from routers.upload import router as upload_router #นำเข้าเส้นทางจากไฟล์ routers.upload
from fastapi.middleware.cors import CORSMiddleware #เพื่อจัดการกับ Cross-Origin Resource Sharing (CORS) เป็นเทคโนโลยีที่อนุญาตให้เว็บแอปพลิเคชันทำงานร่วมกับแหล่งที่มาจากโดเมนอื่นๆ


app = FastAPI() #สร้าง instance ของ FastAPI application


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], #อนุญาตทุกๆ โดเมนให้เข้าถึงข้อมูลจะต้องใช้ *
    allow_credentials=True, #อนุญาตให้ส่ง cookies และ headers ที่เกี่ยวข้องกับ credentials กลับไปยังเซิร์ฟเวอร์
    allow_methods=["*"], #อนุญาตการใช้งานทุก method ใน HTTP request
    allow_headers=["*"], #อนุญาตทุก header ใน HTTP request
)


#กำหนดเส้นทาง routers
app.include_router(index_router, prefix="/index") #เส้นทางทั้งหมดใน index_router จะถูกเรียกผ่าน URL ที่ขึ้นต้นด้วย "/index"
app.include_router(upload_router, prefix="/upload") #เส้นทางทั้งหมดใน upload_router จะถูกเรียกผ่าน URL ที่ขึ้นต้นด้วย "/upload"


@app.get("/", status_code=status.HTTP_200_OK)
async def read_root():
    return {"Hello": "The server is up and running."}
