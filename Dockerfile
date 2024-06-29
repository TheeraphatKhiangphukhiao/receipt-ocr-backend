FROM python:3.11
WORKDIR /app

RUN apt-get update && \
    apt-get install -y tesseract-ocr && \
    pip install --upgrade pip

COPY . /app
RUN pip install -r requirements.txt

EXPOSE 8000
ENV NAME World

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
