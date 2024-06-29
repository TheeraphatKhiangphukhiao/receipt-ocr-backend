import pytesseract #เพื่อเเปลงรูปภาพใบเสร็จรับเงินมาเป็น text

pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract' #กำหนดเส้นทางไปยังที่อยู่ของ tesseract-ocr เพื่อนำมาใช้งาน