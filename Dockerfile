FROM --platform=linux/amd64 python:3.9-slim

WORKDIR /app

COPY ./app ./app
COPY ./input ./input
COPY ./output ./output
COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["python", "app/main.py"]
