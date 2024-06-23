from fastapi import APIRouter, status, UploadFile #เพื่อใช้ในการสร้างเส้นทางของ API
import cv2 as cv #สำหรับประมวลผลภาพล่วงหน้า
import numpy as np
import pytesseract #เพื่อเเปลงรูปภาพใบเสร็จรับเงินมาเป็น text
import re 

router = APIRouter() #สร้าง instance ของ APIRouter เพื่อนำไปใช้ในการกำหนดเส้นทางของ API


#ฟังก์ชันเพื่ออ่านไฟล์รูปภาพที่อัปโหลด โดยใช้ OpenCV เพื่อแปลงภาพเป็น grayscale
async def create_upload_file(file):
    content = await file.read() #อ่านข้อมูลทั้งหมดจากไฟล์ที่ได้รับมาเป็น byte string โดยใช้การอ่านแบบ asynchronous
    nparr = np.frombuffer(content, np.uint8) #เเปลงข้อมูล byte string ในตัวเเปร content เป็น array ของตัวเลข 8-bit unsigned integers
    imRGB = cv.imdecode(nparr, cv.IMREAD_COLOR) #เพื่อเเปลง array ของตัวเลขที่เก็บใน nparr ให้เป็นภาพสี RGB
    imGray = cv.cvtColor(imRGB, cv.COLOR_BGR2GRAY) #แปลงภาพจากรูปแบบสี RGB เป็นภาพสีเทา grayscale
    return imRGB #ส่งรูปภาพกลับไป


#ฟังก์ชั่นสำหรับเเปลงรูปภาพเป็น รูปภาพระดับเทา
async def convert_to_grayscale(image):
    imGray = cv.cvtColor(image, cv.COLOR_BGR2GRAY) #แปลงภาพจากรูปแบบสี RGB เป็นภาพสีเทา grayscale
    return imGray


@router.get("/", status_code=status.HTTP_200_OK)
async def read_makro():
    return {"message": "This is the makro endpoint"}


@router.post("/receipt/ocr", status_code=status.HTTP_200_OK)
async def extract_makro_receipt_information(file: UploadFile):
    imRGB = await create_upload_file(file) #ส่งไฟล์ไปยังฟังก์ชั่น
    imGray = await convert_to_grayscale(imRGB) #ส่งรูปภาพ RGB ไปยังฟังก์ชั่นเพื่อเเปลงเป็นภาพระดับเทา

    imGray = cv.equalizeHist(imGray)
    
    scale_percent = 150
    width = int(imGray.shape[1] * scale_percent / 100)
    height = int(imGray.shape[0] * scale_percent / 100)
    rescaled = cv.resize(imGray, (width, height), interpolation=cv.INTER_LINEAR)

    blur = cv.GaussianBlur(rescaled, (5, 5), 0)
    
    cv.namedWindow('blur', cv.WINDOW_NORMAL)
    cv.imshow('blur', blur) # คำสั่งเเสดงผลภาพ

    cv.waitKey(0) # คำสั่งรอคอยการกด Keyboard
    cv.destroyAllWindows() # เป็นการล้างหน้าต่างทั้งหมดที่เปิดเเสดงผลภาพ 