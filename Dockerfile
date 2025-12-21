FROM python:3.11.14-alpine3.23
LABEL maintainer="kononovb71@gmail.com"

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
