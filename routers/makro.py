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

#ฟังก์ชั่นสำหรับปรับค่า pixel ของภาพให้อยู่ในช่วงที่ต้องการโดยการกำหนดจาก 0 - 255 เป็นค่าความเข้มของสีในระบบ RGB
async def normalize_image(imRGB):
    normalized_image = cv.normalize(imRGB, None, 0, 255, cv.NORM_MINMAX) #None หมายถึงสำหรับสร้าง output array ใหม่
    return normalized_image

#ฟังก์ชั่นสำหรับปรับขนาดรูปภาพให้เป็นขนาดมาตรฐาน เพื่อให้เเน่ใจว่ามีความสมํ่าเสมอ
async def scale_image(image, width):
    scale_ratio = width / image.shape[1] #เอา 800 หารด้วย จำนวนคอลัมน์ของ image ที่เป็นภาพสี RGB
    #ตัวอย่าง หลังจากผ่านคำสั่ง resize
    # shape เริ่มต้น = (3501, 2550, 3) = (row, column, 3)
    # shape ผลลัพธ์ = (1098, 800, 3) = (row, column, 3)
    scaled_image = cv.resize(image, (width, int(image.shape[0] * scale_ratio)))
    return scaled_image

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
    
    #เเปลงภาพระดับเทาให้เป็นภาพเเบบ binary
    #THRESH_BINARY_INV : เเปลงพิกเซลที่มีค่าน้อยกว่า threshold ให้เป็นสีขาว 255 และพิกเซลที่มีค่ามากกว่า threshold ให้เป็นสีดำ 0
    #THRESH_OTSU : คำนวณหา threshold โดยวิธี Otsu
    thresh = cv.threshold(imGray, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1] #คำตอบที่ได้จะเป็น tuple ที่ประกอบด้วยค่า threshold และภาพที่ผ่านการ threshold ซึ่งเราสนใจแค่ภาพเลยใช้ [1] เพื่อเลือกเฉพาะภาพนั้นมาใช้งาน
    print(thresh)
    
    noise_reduced = cv.medianBlur(thresh, 3) #ทำการลด noise โดยใช้ฟิลเตอร์แบบ median blur กับภาพเเละใช้ kernel 3x3

    #เพิ่มความคมชัด
    sharpened = cv.addWeighted(noise_reduced, 1.5, noise_reduced, -0.5, 0)

    #ทำการเพิ่มขนาดของรูปภาพให้ใหญ่ขึ้น 1.5 เท่าในเเกน x เเละ 1.5 เท่าในเเกน y
    #interpolation=cv.INTER_LINEAR : ใช้การ interpolation แบบ linear เพื่อเพิ่มความละเอียดของภาพ
    resized = cv.resize(sharpened, None, fx=1.5, fy=1.5, interpolation=cv.INTER_LINEAR)
    
    # cv.namedWindow('resized', cv.WINDOW_NORMAL)
    # cv.imshow('resized', resized) # คำสั่งเเสดงผลภาพ
    # cv.waitKey(0) # คำสั่งรอคอยการกด Keyboard
    # cv.destroyAllWindows() # เป็นการล้างหน้าต่างทั้งหมดที่เปิดเเสดงผลภาพ 
    
    text = pytesseract.image_to_string(resized, lang='Tha+Eng') #เเปลงรูปภาพใบเสร็จไปเป็น text
    text = text.splitlines() #เเบ่งบรรทัดตามการขึ้นบรรทัดใหม่ \n
    
    for index in range(len(text)):
        if re.compile(r'^\d+\s+\d{13}').search(text[index]):
            print(text[index])
        elif re.compile(r'ชำระโดย').search(text[index]):
            print(text[index])
            break
