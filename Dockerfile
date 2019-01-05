FROM python:3.7-alpine

COPY . /app
WORKDIR /app
ENV PYTHONPATH=/app

RUN pip install -r requirements.txt
