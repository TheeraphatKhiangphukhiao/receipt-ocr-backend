from typing import Union
from fastapi import FastAPI, status
from routers.lotus import router as lotus_router #นำเข้าเส้นทางจากไฟล์ routers.lotus
from routers.bigc import router as bigc_router #นำเข้าเส้นทางจากไฟล์ routers.bigc
from routers.makro import router as makro_router #นำเข้าเส้นทางจากไฟล์ routers.makro
from routers.index import router as index_router #นำเข้าเส้นทางจากไฟล์ routers.index
from fastapi.middleware.cors import CORSMiddleware #เพื่อจัดการกับ Cross-Origin Resource Sharing (CORS) เป็นเทคโนโลยีที่อนุญาตให้เว็บแอปพลิเคชันทำงานร่วมกับแหล่งที่มาจากโดเมนอื่นๆ

app = FastAPI() #สร้าง instance ของ FastAPI application

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #อนุญาตทุกๆ โดเมนให้เข้าถึงข้อมูล
    allow_credentials=True, #อนุญาตให้ส่ง cookies และ headers ที่เกี่ยวข้องกับ credentials กลับไปยังเซิร์ฟเวอร์
    allow_methods=["*"], #อนุญาตการใช้งานทุก method ใน HTTP request
    allow_headers=["*"], #อนุญาตทุก header ใน HTTP request
)

#กำหนดเส้นทาง routers
app.include_router(index_router, prefix="/index") #เส้นทางทั้งหมดใน index_router จะถูกเรียกผ่าน URL ที่ขึ้นต้นด้วย "/index"
app.include_router(lotus_router, prefix="/lotus") #เส้นทางทั้งหมดใน lotus_router จะถูกเรียกผ่าน URL ที่ขึ้นต้นด้วย "/lotus"
app.include_router(bigc_router, prefix="/bigc") #เส้นทางทั้งหมดใน bigc_router จะถูกเรียกผ่าน URL ที่ขึ้นต้นด้วย "/bigc"
app.include_router(makro_router, prefix="/makro") #เส้นทางทั้งหมดใน makro_router จะถูกเรียกผ่าน URL ที่ขึ้นต้นด้วย "/makro"

@app.get("/", status_code=status.HTTP_200_OK)
async def read_root():
    return {"Hello": "The server is up and running."}
