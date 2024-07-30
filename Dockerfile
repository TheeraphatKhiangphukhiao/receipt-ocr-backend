FROM python:3.11-bookworm

RUN apt-get update && \
    apt-get install -y wget unzip bc vim libleptonica-dev

RUN apt-get install -y --reinstall make && \
    apt-get install -y g++ autoconf automake libtool pkg-config \
    libpng-dev libjpeg62-turbo-dev libtiff5-dev libicu-dev \
    libpango1.0-dev autoconf-archive

WORKDIR /app

RUN mkdir src && cd /app/src && \
    wget https://github.com/tesseract-ocr/tesseract/archive/refs/tags/5.4.1.zip && \
    unzip 5.4.1.zip && \
    cd /app/src/tesseract-5.4.1 && ./autogen.sh && ./configure && make && make install && ldconfig && \
    cd /usr/local/share/tessdata && wget https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata && \
    cd /usr/local/share/tessdata && wget https://github.com/tesseract-ocr/tessdata_best/raw/main/tha.traineddata

ENV TESSDATA_PREFIX=/usr/local/share/tessdata

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./main.py /code/
COPY ./csvfile /code/csvfile
COPY ./routers /code/routers
COPY ./uploads /code/uploads

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]