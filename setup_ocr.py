import pytesseract #เพื่อเเปลงรูปภาพใบเสร็จรับเงินมาเป็น text

pytesseract.pytesseract.tesseract_cmd = r'modules\Tesseract-OCR\tesseract.exe' #กำหนดเส้นทางไปยังที่อยู่ของ tesseract-ocr