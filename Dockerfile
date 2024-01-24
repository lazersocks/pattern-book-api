FROM python:latest
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install -r requirements.txt

