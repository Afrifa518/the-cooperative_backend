FROM python:3.8.10-slim

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000

CMD uvicorn main:app --port=8000 --host=0.0.0.0