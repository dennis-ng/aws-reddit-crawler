FROM python:3.9.6-slim-buster

WORKDIR /app
COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD ["python", "reddit-wsb-crawler.py"]