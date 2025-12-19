FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . /app

COPY ./config/config.yaml ./config/
COPY ./config/.env ./config/
COPY ./db/migrations/ /app/db/migrations/
RUN chmod -R 755 /app/db/migrations
RUN chmod +x apply_migrations.sh

EXPOSE 8080

ENTRYPOINT ["./apply_migrations.sh"]

CMD ["python3", "cmd/main.py"]