from fastapi import APIRouter, status, UploadFile #เพื่อใช้ในการสร้างเส้นทางของ API
import cv2 as cv #สำหรับประมวลผลภาพล่วงหน้า
import numpy as np
import re 
import pytesseract #เพื่อเเปลงรูปภาพใบเสร็จรับเงินมาเป็น text
from . import makro #ทำการ import ไฟล์ makro.py เข้ามา, . หมายถึงโฟลเดอร์เดียวกันกับไฟล์ที่กำลังเขียนอยู่
from . import lotus 
from . import bigc
from PIL import Image
from io import BytesIO


router = APIRouter() #สร้าง instance ของ APIRouter เพื่อนำไปใช้ในการกำหนดเส้นทางของ API


#ฟังก์ชันเพื่ออ่านไฟล์รูปภาพที่อัปโหลด โดยใช้ OpenCV เพื่อแปลงภาพเป็น grayscale
async def create_upload_file(file):
    content = await file.read() #อ่านข้อมูลทั้งหมดจากไฟล์ที่ได้รับมาเป็น byte string โดยใช้การอ่านแบบ asynchronous
    image = Image.open(BytesIO(content)) #เเปลง byte string ไปเป็นรูปภาพ
    image = np.array(image)

    return image
    

#thresholding
async def thresholding(imGray):
    thresh = cv.threshold(imGray, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)[1] #เเปลงรูปภาพเป็นเเบบ 2 ระดับในที่นี้คือ 0 กับ 255 โดยใช้วิธีการเเปลงเเบบ Otsu
    return thresh


#Grayscale image
async def convert_to_grayscale(image):
    imGray = cv.cvtColor(image, cv.COLOR_BGR2GRAY) #แปลงภาพจากรูปแบบสี RGB เป็นภาพสีเทา grayscale
    return imGray


@router.get("/", status_code=status.HTTP_200_OK)
async def read_index():
    return {"message": "This is the index endpoint"}


#เส้นทางสำหรับ preprocess รูปภาพเเละเเปลงรูปภาพใบเสร็จมาเป็น text รวมถึงตรวจสอบว่าเป็นใบเสร็จประเภทใด
@router.post("/receipt/ocr", status_code=status.HTTP_200_OK)
async def extract_receipt_information(file: UploadFile):

    image = await create_upload_file(file) #ส่งไฟล์ไปยังฟังก์ชั่น

    imGray = await convert_to_grayscale(image) #ส่งรูปภาพ RGB ไปยังฟังก์ชั่นเพื่อเเปลงเป็นภาพ grayscale

    blur = cv.GaussianBlur(imGray, (5, 5), 0)


    text = pytesseract.image_to_string(blur, lang='tha+eng') #เเปลงรูปภาพใบเสร็จไปเป็น text
    

    #re.compile ใช้ในการสร้างวัตถุ regular expression
    makro_pattern = re.compile(r'\bmakro\b') #\bmakro\b จะค้นหาคำว่า makro ในตัวเเปร text โดยคำนี้จะต้องมีขอบเขตของคำ word boundary ที่ขึ้นต้นเเละลงท้ายโดยใช้ \b
    bigc_pattern = re.compile(r'บิ๊กซี') #สร้าง pattern ที่จะค้นหาคำว่า บิ๊กซี ในตัวเเปร text
    lotus_pattern = re.compile(r'เอก-ชัย ดีสทริบิวชั่น ซิสเทม') #สร้าง pattern ที่จะค้นหาคำว่า เอก-ชัย ดีสทริบิวชั่น ซิสเทม ในตัวเเปร text


    if makro_pattern.search(text): #เป็นการตรวจสอบว่าในตัวเเปร text มีคำว่า makro หรือไม่
        result = await makro.extract_makro_receipt_information(text) #เเสดงว่ารูปภาพนี้คือ makro ทำการส่งข้อมูลไปสกัดข้อมูลส่วนสำคัญออกมา

    elif bigc_pattern.search(text):
        result = await bigc.extract_bigc_receipt_information(text)

    elif lotus_pattern.search(text):
        result = await lotus.extract_lotus_receipt_information(text) #เเสดงว่ารูปภาพนี้คือ lotus ทำการส่งข้อมูลไปสกัดข้อมูลส่วนสำคัญออกมา

    else:
        result = "not found" 


    return {"result": result} #ส่งข้อมูลส่วนสำคัญกลับไปในรูปเเบบ json