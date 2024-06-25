from fastapi import APIRouter, status, Request, HTTPException #เพื่อใช้ในการสร้างเส้นทางของ API
import csv
from fastapi.responses import StreamingResponse, FileResponse

router = APIRouter() #สร้าง instance ของ APIRouter เพื่อนำไปใช้ในการกำหนดเส้นทางของ API


@router.get("/", status_code=status.HTTP_200_OK)
async def read_upload():
    return {"message": "This is the upload endpoint"}
 

@router.post("/save/receipt", status_code=status.HTTP_201_CREATED)
async def save_receipt(Receipt_data: Request):
    items = await Receipt_data.json() 
    all_keys = set()
    for item in items['result']: 
        if isinstance(item, dict):
            all_keys.update(item.keys())
    sorted_keys = sorted(all_keys)
    # data rows of csv file
    rows = []
    for item in items['result']: 
        row = [item.get(key, '') for key in sorted_keys]
        rows.append(row)
      
    filename = r"uploads\Receipt.csv"
    with open(filename, 'w', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        #csvwriter.writerow([items['result'][0]['item1']])
        csvwriter.writerows(rows)
    try:
        return FileResponse(path=filename, media_type='text/csv', filename=filename)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found.")