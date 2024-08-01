from fastapi import APIRouter, status, UploadFile #เพื่อใช้ในการสร้างเส้นทางของ API
import numpy as np
import re 
import pytesseract #เพื่อเเปลงรูปภาพใบเสร็จรับเงินมาเป็น text
from . import makro #ทำการ import ไฟล์ makro.py เข้ามา, . หมายถึงโฟลเดอร์เดียวกันกับไฟล์ที่กำลังเขียนอยู่
from . import lotus 
from . import bigc
import cv2

router = APIRouter() #สร้าง instance ของ APIRouter เพื่อนำไปใช้ในการกำหนดเส้นทางของ API

#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


#เส้นทางสำหรับ preprocess รูปภาพเเละเเปลงรูปภาพใบเสร็จมาเป็น text รวมถึงตรวจสอบว่าเป็นใบเสร็จประเภทใด
@router.post("/receipt/ocr", status_code=status.HTTP_200_OK)
async def extract_receipt_information(file: UploadFile):

    result = []

    makro_pattern = r'บริษัท ซีพี แอ็กซ์ตร้า'
    bigc_pattern = r'บิ๊กซี'
    lotus_pattern = r'บริษัท เอก-ชัย'
    
    contents = await file.read() #อ่านข้อมูลทั้งหมดจากไฟล์

    bin_img = preprocessing(contents)


    text = pytesseract.image_to_string(bin_img, lang='tha+eng', config='--psm 6') #เเปลงรูปภาพใบเสร็จไปเป็น text
    print(text)

    if re.search(makro_pattern, text):
        print('Hello makro !!')

        result = await makro.extract_makro_receipt_information(text)

    elif re.search(bigc_pattern, text):
        print('Hello big c !!')

        result = await bigc.extract_bigc_receipt_information(text)

    elif re.search(lotus_pattern, text):
        print('Hello lotus !!')

        result = await lotus.extract_lotus_receipt_information(text)

    else:
        print('รูปภาพไม่ถูกต้อง ต้องเป็น makro bigc lotus เท่านั้น')


    return {
        "result": result
    }


#ฟังก์ชั่นสำหรับประมวลผลภาพล่วงหน้า
def preprocessing(contents):
    image_path = r'uploads\image_processing.jpg'

    nparr = np.fromstring(contents, np.uint8)
    imRGB = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    r_imRGB = cv2.resize(imRGB, None, fx=2, fy=2)

    imGray = cv2.cvtColor(r_imRGB, cv2.COLOR_BGR2GRAY)
    bin_img = cv2.threshold(imGray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    cv2.imwrite(image_path, bin_img) #เขียนไฟล์ที่ผ่านการประมวลผลเเล้ว

    return bin_img
