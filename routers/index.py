from fastapi import APIRouter, status, UploadFile #เพื่อใช้ในการสร้างเส้นทางของ API
import numpy as np
import re 
import pytesseract #เพื่อเเปลงรูปภาพใบเสร็จรับเงินมาเป็น text
from pytesseract import Output
import io
from . import makro #ทำการ import ไฟล์ makro.py เข้ามา, . หมายถึงโฟลเดอร์เดียวกันกับไฟล์ที่กำลังเขียนอยู่
from . import lotus 
from . import bigc
from PIL import Image, ImageFilter


router = APIRouter() #สร้าง instance ของ APIRouter เพื่อนำไปใช้ในการกำหนดเส้นทางของ API


#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


#เส้นทางสำหรับ preprocess รูปภาพเเละเเปลงรูปภาพใบเสร็จมาเป็น text รวมถึงตรวจสอบว่าเป็นใบเสร็จประเภทใด
@router.post("/receipt/ocr", status_code=status.HTTP_200_OK)
async def extract_receipt_information(file: UploadFile):

    result = []

    image_path = r'uploads\image_processing.jpg'

    makro_pattern = r'บริษัท ซีพี แอ็กซ์ตร้า'
    bigc_pattern = r'บิ๊กซี'
    lotus_pattern = r'บริษัท เอก-ชัย'
    

    contents = await file.read()

    imRGB = Image.open(io.BytesIO(contents))
    print(imRGB.mode)
    

    imGray = imRGB.convert('L')
    print(imGray.mode)

    r_img = imGray.resize((1191, 2000), Image.LANCZOS)

    f_img = r_img.filter(ImageFilter.UnsharpMask(radius=6.8, percent=150, threshold=0))

    f_img.save(image_path, quality=100)


    image = Image.open(image_path)
    width, height = image.size

    conv_img = np.array(image)


    text = pytesseract.image_to_string(conv_img, lang='tha') #เเปลงรูปภาพใบเสร็จไปเป็น text
    print(text)

    if re.search(makro_pattern, text):
        print('Hello makro !!')

        upper_part = re.compile(r'WEIGHT')
        lower_part = re.compile(r'KBANK')

        left, top, right, bottom = image_crop_area(conv_img, upper_part, lower_part, width)

        image = image.crop((left, top, right, bottom))
        #image.show()
        image = np.array(image)


        #โหมดการเเบ่งหน้า tesseract (psm) วิธีปรับปรุงความเเม่นยำของ OCR
        makro_text = pytesseract.image_to_string(image, lang='tha+eng', config='--psm 6') #เเปลงรูปภาพใบเสร็จไปเป็น text
        print(makro_text)

        result = await makro.extract_makro_receipt_information(makro_text)

    elif re.search(bigc_pattern, text):
        print('Hello big c !!')

        upper_part = re.compile(r'POS')
        lower_part = re.compile(r'Payment')

        left, top, right, bottom = image_crop_area(conv_img, upper_part, lower_part, width)

        image = image.crop((left, top, right, bottom))
        #image.show()
        image = np.array(image)


        bigc_text = pytesseract.image_to_string(image, lang='tha+eng', config='--psm 6') #เเปลงรูปภาพใบเสร็จไปเป็น text
        print(bigc_text)

        result = await bigc.extract_bigc_receipt_information(bigc_text)

    elif re.search(lotus_pattern, text):
        print('Hello lotus !!')

        lotus_text = pytesseract.image_to_string(conv_img, lang='tha+eng', config='--psm 6') #เเปลงรูปภาพใบเสร็จไปเป็น text

        result = await lotus.extract_lotus_receipt_information(lotus_text)

    else:
        print('รูปภาพไม่ถูกต้อง ต้องเป็น makro bigc lotus เท่านั้น')
        result = []


    return {
        "result": result
    }



#ฟังก์ชั่นหาพื้นที่สำหรับ ตัดรูปภาพเอาเฉพาะส่วนสำคัญ
def image_crop_area(conv_img, upper_part, lower_part, width):

    x1, y1, w1, h1 = 0, 0, 0, 0
    x2, y2, w2, h2 = 0, 0, 0, 0

    d = pytesseract.image_to_data(conv_img, lang='eng', output_type=Output.DICT)
    print(d.keys())
    print(d['text'])

    n_boxes = len(d['text'])

    for index in range(n_boxes):

        if upper_part.search(d['text'][index]):

            print('Hello Upper !!')
            print(d['text'][index])

            (x1, y1) = (d['left'][index], d['top'][index])
            (w1, h1) = (d['width'][index], d['height'][index])

            break

    for index in range(n_boxes):

        if lower_part.search(d['text'][index]):

            print('Hello Lower !!')
            print(d['text'][index])

            (x2, y2) = (d['left'][index], d['top'][index])
            (w2, h2) = (d['width'][index], d['height'][index])

            break

    left = 0
    top = y1+h1
    right = width
    bottom = ((y2+h2)+5)

    return left, top, right, bottom
    
