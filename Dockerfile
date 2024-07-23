FROM python:3.11-slim-bullseye

WORKDIR /code

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-tha \
    libgl1-mesa-glx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata/

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./main.py /code/
COPY ./csvfile /code/csvfile
COPY ./routers /code/routers
COPY ./uploads /code/uploads

ENV PYTHONPATH "${PYTHONPATH}:/code"
CMD ["fastapi", "run", "main.py", "--port", "80"]