FROM python:3.12-alpine

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN python -m pip install --upgrade pip

RUN pip install --upgrade -r /app/requirements.txt -v

COPY ./mysite /app/mysite
