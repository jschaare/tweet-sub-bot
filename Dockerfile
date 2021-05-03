FROM python:3.9-alpine

RUN apk update && apk upgrade
RUN apk add --no-cache git make build-base linux-headers

WORKDIR /code

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY config.json ./config.json
COPY . .