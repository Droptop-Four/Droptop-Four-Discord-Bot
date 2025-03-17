FROM python:3.13-alpine

WORKDIR /droptop_bot

COPY . .

RUN apk update && apk add \
    jpeg-dev \
    zlib-dev \
    libpng-dev \
    && rm -rf /var/cache/apk/*

RUN pip install -r requirements.txt

CMD ["python", "main.py"]