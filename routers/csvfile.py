from fastapi import APIRouter, status, Request, HTTPException #เพื่อใช้ในการสร้างเส้นทางของ API
import csv #สำหรับอ่านเเละเขียนไฟล์ csv โดยมีฟังก์ชันเเละคลาสต่างๆ ที่ช่วยให้การทำงานกับไฟล์ csv ง่ายขึ้น
from fastapi.responses import FileResponse #สำหรับส่งไฟล์กลับไปยังผู้เรียก API ซึ่งทำให้ง่ายต่อการส่งไฟล์ประเภทต่างๆ เช่น รูปภาพ csv เอกสาร หรือไฟล์อื่นๆ

router = APIRouter() #สร้าง instance ของ APIRouter เพื่อนำไปใช้ในการกำหนดเส้นทางของ API


@router.get("/", status_code=status.HTTP_200_OK)
async def read_csvfile():
    return {"message": "This is the csvfile endpoint"}
 

#เส้นทางสำหรับนำข้อมูลส่วนสำคัญของใบเสร็จมาเขียนเป็นไฟล์ csv เเละส่งไฟล์นั้นกลับไปยังผู้เรียก API
@router.post("/save/receipt", status_code=status.HTTP_201_CREATED)
async def save_receipt(receipt_data: Request):

    items = await receipt_data.json() #ดึงข้อมูลจากตัวเเปร receipt_data ในรูปเเบบ json 
    print(items)
    
    all_keys = set() #ประกาศตัวเเปรชนิด set, set นั้นจะมีสมาชิกไม่ซํ้ากัน, set ไม่มีการจัดเรียงลำดับของสมาชิก, สามารถเพิ่มหรือลบสมาชิกใน set ได้
    print(all_keys) #set()


    for item in items['result']: #วนลูปนำข้อมูล json เเต่ละเเถวของ result ออกมา, ซึ่ง result มีชนิดเป็น List ที่เก็บ json หลายๆตัว
    
        if isinstance(item, dict): #ตรวจสอบว่าตัวเเปร item มีชนิดเป็น dictionary หรือไม่
            all_keys.update(item.keys()) #ถ้าเป็นจริงทำการเพิ่ม key ของข้อมูล json เเต่ละเเถว

    sorted_keys = sorted(all_keys) #เรียงลำดับสมาชิกทั้งหมดในตัวเเปร all_keys เเล้วเก็บไว้ในตัวเเปร sorted_keys


    rows = [] #ประกาศตัวเเปร List สำหรับเก็บข้อมูลเป็นตาราง
    for item in items['result']: #วนลูปนำข้อมูล json เเต่ละเเถวของ result ออกมา, ซึ่ง result มีชนิดเป็น List ที่เก็บ json หลายๆตัว

        row = [item.get(key, '') for key in sorted_keys] #ดึงค่าของ item โดยใช้ key
        rows.append(row) #ทำการเพิ่มข้อมูลทีละเเถวเข้าไปที่ rows, คำตอบจะได้เป็น List ซ้อน List


    filename = r"csvfile\receipt.csv" #ที่อยู่สำหรับเก็บไฟล์ 


    with open(filename, 'w', newline='', encoding='utf-8') as csvfile: #w หมายถึงโหมดเขียน, newline='' หมายถึงไม่ให้เพิ่มบรรทัดว่างโดยอัตโนมัติเมื่อเขียนลงไฟล์
        csvwriter = csv.writer(csvfile) #สร้างอ็อบเจกต์สำหรับเขียนข้อมูลลงในไฟล์ csv
        csvwriter.writerows(rows) #เขียนข้อมูลหลายๆเเถวลงในไฟล์ csv
    try:
        return FileResponse(path=filename, media_type='text/csv', filename=filename)
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found.")