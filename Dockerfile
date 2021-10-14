FROM python:3.10-alpine
LABEL author='dahyor'

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt

WORKDIR /code
COPY . /code

RUN adduser -D dahyor
USER dahyor
