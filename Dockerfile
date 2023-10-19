FROM python:3.9-slim
WORKDIR /docker
COPY requirements.txt requirements.txt
RUN apt-get update
RUN pip3 install -r requirements.txt
COPY . .
