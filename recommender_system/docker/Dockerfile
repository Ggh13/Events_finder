FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /app

COPY ./config/.env ./config/

EXPOSE 8000

CMD ["python3", "main.py"]