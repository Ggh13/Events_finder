FROM python:3.13-slim

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt
COPY ./config/.env ./config/

EXPOSE 8001

CMD ["python3", "main.py"]