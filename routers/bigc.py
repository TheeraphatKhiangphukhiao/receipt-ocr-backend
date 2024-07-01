from fastapi import APIRouter, status, UploadFile #เพื่อใช้ในการสร้างเส้นทางของ API
import cv2 as cv #สำหรับประมวลผลภาพล่วงหน้า
import numpy as np
import re 
import pytesseract #เพื่อเเปลงรูปภาพใบเสร็จรับเงินมาเป็น text


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
async def read_bigc():
    return {"message": "This is the big c endpoint"}


@router.post("/receipt/ocr", status_code=status.HTTP_200_OK)
async def extract_bigc_receipt_information(file: UploadFile):
    result = [] #ประกาศตัวเเปรสำหรับเก็บข้อมูลของใบเสร็จตาม pattern ที่กำหนด

    imRGB = await create_upload_file(file) #ส่งไฟล์ไปยังฟังก์ชั่น
    imGray = await convert_to_grayscale(imRGB) #ส่งรูปภาพ RGB ไปยังฟังก์ชั่นเพื่อเเปลงเป็นภาพระดับเทา
    
    # #เเปลงภาพระดับเทาให้เป็นภาพเเบบ binary
    # #THRESH_BINARY_INV : เเปลงพิกเซลที่มีค่าน้อยกว่า threshold ให้เป็นสีขาว 255 และพิกเซลที่มีค่ามากกว่า threshold ให้เป็นสีดำ 0
    # #THRESH_OTSU : คำนวณหา threshold โดยวิธี Otsu
    # thresh = cv.threshold(imGray, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1] #คำตอบที่ได้จะเป็น tuple ที่ประกอบด้วยค่า threshold และภาพที่ผ่านการ threshold ซึ่งเราสนใจแค่ภาพเลยใช้ [1] เพื่อเลือกเฉพาะภาพนั้นมาใช้งาน
    # print(thresh)
    
    # noise_reduced = cv.medianBlur(thresh, 3) #ทำการลด noise โดยใช้ฟิลเตอร์แบบ median blur กับภาพเเละใช้ kernel 3x3

    # #เพิ่มความคมชัด
    # sharpened = cv.addWeighted(noise_reduced, 1.5, noise_reduced, -0.5, 0)

    # #ทำการเพิ่มขนาดของรูปภาพให้ใหญ่ขึ้น 1.5 เท่าในเเกน x เเละ 1.5 เท่าในเเกน y
    # #interpolation=cv.INTER_LINEAR : ใช้การ interpolation แบบ linear เพื่อเพิ่มความละเอียดของภาพ
    # resized = cv.resize(sharpened, None, fx=1.5, fy=1.5, interpolation=cv.INTER_LINEAR)
    
    # # cv.namedWindow('resized', cv.WINDOW_NORMAL)
    # # cv.imshow('resized', resized) # คำสั่งเเสดงผลภาพ
    # # cv.waitKey(0) # คำสั่งรอคอยการกด Keyboard
    # # cv.destroyAllWindows() # เป็นการล้างหน้าต่างทั้งหมดที่เปิดเเสดงผลภาพ 
    
    text = pytesseract.image_to_string(imGray, lang='tha+eng') #เเปลงรูปภาพใบเสร็จไปเป็น text
    text = text.splitlines() #เเบ่งบรรทัดตามการขึ้นบรรทัดใหม่ \n
    
    #กำหนด pattern สำหรับเก็บข้อมูล
    result.append({
        "item1": "จำนวน",
        "item2": "รหัสสินค้า",
        "item3": "รายการสินค้า",
        "item4": "หน่วยบรรจุ",
        "item5": "ราคาต่อหน่วย (รวม VAT)",
        "item6": "ส่วนลด บาท",
        "item7": "VAT CODE",
        "item8": "จำนวนเงิน (รวม VAT)"
    })
    
    for index in range(len(text)): #วนลูปตามความยาวของตัวเเปร text ที่มีชนิดเป็น List 
        number = 0 #ประกาศตัวเเปรสำหรับเก็บจำนวนของบรรทัดที่จะบวกไปหาข้อมูลที่เกินของรายการสินค้าในเเถวนั้นๆ
        over = "" #สำหรับเก็บข้อมูลที่เกินของรายการสินค้าในเเถวนั้นๆออกมา
        product_name = "" #ประกาศตัวเเปรสำหรับสร้างรายการสินค้าที่มีการ join ข้อมูลใน List

        if re.compile(r'^\d+.\d+\s+\d{13}').search(text[index]): #หาเเถวที่ต้องการ
            words = text[index].split() #เเบ่งข้อความตามการเว้นวรรค
            print(words)
            
            count = 1 #สำหรับนับจำนวนของบรรทัดที่จะบวกไปหาข้อมูลที่เกินของรายการสินค้าในเเถวนั้นๆ
            while True: 
                if text[index+count] == "": #ตรวจสอบว่าบรรทัดต่อๆไปของเเถวนั้นๆมีค่าว่างหรือไม่
                    count += 1 #ถ้ามีค่าว่างที่ให้ count บวกไปทีละ 1 เเล้ววนลูปไปเรื่อยๆจนกว่าจะเจอเเถวที่มีข้อมูล
                else:
                    number += count #ถ้าเจอเเถวมีข้อมูลก็ให้เก็บจำนวนของบรรทัดที่จะบวกไปหาข้อมูลที่เกินของรายการสินค้าในเเถวนั้นๆ เเละหยุดการทำงานของลูป
                    break

            if (not re.compile(r'^\d+.\d+\s+\d{13}').search(text[index+number])) and (not re.compile(r'ออกแทนใบกํากับภาษีอย่างย่อ\s+เลขที่\s+\d+').search(text[index+number])):
                over = text[index+number] #นำข้อมูลที่เกินของรายการสินค้าในเเถวนั้นๆออกมา
                product_name = " ".join(words[2:-3]) + over #นำข้อมูลที่เกินมาต่อเข้ากับรายการสินค้าของตัวมัน

            else: #กรณีที่ไม่มีข้อความเกินจนขึ้นบรรทัดใหม่
                print("กรณีที่ไม่มีข้อความเกินจนขึ้นบรรทัดใหม่")
                product_name = " ".join(words[2:-3]) #เพิ่มรายการสินค้า, การ join หมายความว่านำข้อมูลใน List มารวมกันเเละเเทนที่ช่องที่ต่อกันด้วย " " หรือจะใส่ "-"

            result.append({
                "item1": words[0], #เพิ่มจำนวน
                "item2": words[1], #เพิ่มรหัสสินค้า
                "item3": product_name, #เพิ่มรายการสินค้า
                "item4": "", #เนื่องจากใบเสร็จ big c ไม่มี column สำหรับข้อมูลหน่วยบรรจุ ดังนั้นจึงใส่ค่าว่าง
                "item5": words[-3], #เพิ่มราคาต่อหน่วย (รวม VAT), การใช้ตัวเลขติดลบในการเข้าถึงสมาชิกของ List จะเป็นการเข้าถึงสมาชิกจากท้ายสุดมา -3 หมายถึงสมาชิกตัวที่สามจากด้านท้ายสุดของ List
                "item6": words[-2], #เพิ่มส่วนลด บาท, -2 หมายถึงสมาชิกตัวที่ 2 จากด้านท้ายสุดของ List
                "item7": "", #เนื่องจากใบเสร็จ big c ไม่มี column สำหรับข้อมูล VAT CODE ดังนั้นจึงใส่ค่าว่าง
                "item8": words[-1] #เพิ่มจำนวนเงิน (รวม VAT), -1 หมายถึงสมาชิกตัวเเรกจากด้านท้ายสุดของ List
            })
            
        elif re.compile(r'ออกแทนใบกํากับภาษีอย่างย่อ\s+เลขที่\s+\d+').search(text[index]): #\s หมายถึง whitespace, \s+ ต้องมี whitespace อย่างน้อยหนึ่งขึ้นไป
            break #ถ้าวนลูปจนถึงเเถวที่ไม่ต้องการ ทำการหยุดลูป

    json = {"result": result} #สร้างข้อมูล json สำหรับส่งไปเขียนไฟล์ csv

    return {"result": result}
