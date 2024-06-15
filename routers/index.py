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
    return imGray #ส่งรูปภาพกลับไป

@router.get("/", status_code=status.HTTP_200_OK)
async def read_index():
    return {"message": "This is the index endpoint"}

#เส้นทางสำหรับ preprocess รูปภาพเเละเเปลงรูปภาพใบเสร็จมาเป็น text รวมถึงตรวจสอบว่าเป็นใบเสร็จประเภทใด
@router.post("/receipt/identify", status_code=status.HTTP_200_OK)
async def identify_receipt_type(file: UploadFile):
    receipt_type_name: str = "" #ตัวเเปรสำหรับเก็บชื่อประเภทของใบเสร็จ
    
    imGray = await create_upload_file(file) #ส่งไฟล์ไปยังฟังก์ชั่น
    blur = cv.GaussianBlur(imGray, (5, 5), 0)
    text = pytesseract.image_to_string(blur, lang='Tha+Eng') #เเปลงรูปภาพใบเสร็จไปเป็น text
    
    #re.compile ใช้ในการสร้างวัตถุ regular expression
    makro_pattern = re.compile(r'\bmakro\b') #\bmakro\b จะค้นหาคำว่า makro ในตัวเเปร text โดยคำนี้จะต้องมีขอบเขตของคำ word boundary ที่ขึ้นต้นเเละลงท้ายโดยใช้ \b
    bigc_pattern = re.compile(r'บิ๊กซี') #สร้าง pattern ที่จะค้นหาคำว่า บิ๊กซี ในตัวเเปร text

    if makro_pattern.search(text): #เป็นการตรวจสอบว่าในตัวเเปร text มีคำว่า makro หรือไม่
        receipt_type_name = "makro" #ถ้าพบก็กำหนดให้เป็น makro
    elif bigc_pattern.search(text):
        receipt_type_name = "bigc"
    else:
        receipt_type_name = "lotus" #เนื่องจากใบเสร็จ lotus ไม่มี keyword ที่บ่งบอกว่าเป็นใบเสร็จประเภทใด เเต่ในโครงการนี้มีใบเสร็จเเค่ 3 ประเภท เเละอีกสองประเภทมี keyword ที่บ่งบอกว่าเป็นใบเสร็จประเภทใด ดังนั้นเมื่อไม่เข้าเงื่อนไขใดเลยจึงกลายเป็นประเภท lotus เเน่นอน

    return {"receipt_type_name": receipt_type_name} #ส่งประเภทของใบเสร็จรับเงินไปให้ front end