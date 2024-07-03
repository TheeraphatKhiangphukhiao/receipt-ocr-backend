import re 


async def extract_makro_receipt_information(text):

    result = [] #ประกาศตัวเเปรสำหรับเก็บข้อมูลของใบเสร็จตาม pattern ที่กำหนด
    payment_amount: int = 0

    text = text.splitlines() #เเบ่งบรรทัดตามการขึ้นบรรทัดใหม่ \n

    #กำหนดชื่อบริษัท
    result.append({
        "item1": "บริษัท ซีพี เเอ็กซ์ตร้า จำกัด (มหาชน)"
    })
    

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

        if re.compile(r'^\d+\s+\d{13}').search(text[index]):

            words = text[index].split() #เเบ่งข้อความตามการเว้นวรรค
            print(words)

            
            result.append({
                "item1": words[0], #เพิ่มจำนวน
                "item2": words[1], #เพิ่มรหัสสินค้า
                "item3": " ".join(words[2:-4]), #เพิ่มรายการสินค้า, การ join หมายความว่านำข้อมูลใน List มารวมกันเเละเเทนที่ช่องที่ต่อกันด้วย " " หรือจะใส่ "-"
                "item4": words[-4], #เพิ่มหน่วยบรรจุ, -4 หมายถึงสมาชิกตัวที่ 4 จากด้านท้ายสุดของ List
                "item5": words[-3], #เพิ่มราคาต่อหน่วย (รวม VAT), การใช้ตัวเลขติดลบในการเข้าถึงสมาชิกของ List จะเป็นการเข้าถึงสมาชิกจากท้ายสุดมา -3 หมายถึงสมาชิกตัวที่สามจากด้านท้ายสุดของ List
                "item6": "", #เนื่องจากใบเสร็จ makro ไม่มี column สำหรับข้อมูล ส่วนลด บาท ดังนั้นจึงใส่ค่าว่าง
                "item7": words[-2], #เพิ่มข้อมูล VAT CODE, -2 หมายถึงสมาชิกตัวที่สองจากด้านท้ายสุดของ List
                "item8": words[-1] #เพิ่มจำนวนเงิน (รวม VAT), -1 หมายถึงสมาชิกตัวเเรกจากด้านท้ายสุดของ List
            })

            payment_amount += float(words[-1])
            
        elif re.compile(r'ชำระโดย').search(text[index]):
            print("หยุดการทำงานของ makro")

            break #ถ้าวนลูปจนถึงเเถวที่ไม่ต้องการ ทำการหยุดลูป


    result.append({
        "item1": "ยอดเงินชำระ",
        "item2": "",
        "item3": "",
        "item4": "",
        "item5": "",
        "item6": "",
        "item7": "",
        "item8": "{:.2f}".format(payment_amount)
    })

    return result
