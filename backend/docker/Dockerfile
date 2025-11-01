FROM python:3.13-slim

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt
COPY ./config/config.yaml ./config/
COPY ./config/.env ./config/
COPY ./db/migrations/ /app/db/migrations/
RUN chmod -R 755 /app/db/migrations

EXPOSE 8080

CMD ["python3", "cmd/main.py"]