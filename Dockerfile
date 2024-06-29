FROM python:3.11-slim-buster
WORKDIR /app

RUN apt-get update && \
    apt-get -qq -y install tesseract-ocr && \
    apt-get -qq -y install libtesseract-dev

COPY . /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

EXPOSE 8000
ENV NAME World

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
