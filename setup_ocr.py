import pytesseract #เพื่อเเปลงรูปภาพใบเสร็จรับเงินมาเป็น text
import os

pytesseract.pytesseract.tesseract_cmd = os.getenv('PYTESSERACT_CMD', '/usr/bin/tesseract') #กำหนดเส้นทางไปยังที่อยู่ของ tesseract-ocr เพื่อนำมาใช้งาน