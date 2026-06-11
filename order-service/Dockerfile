FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY order_service /app

EXPOSE 8000
CMD ["sh", "-c", "until python manage.py migrate --noinput; do echo 'Waiting for order-db...'; sleep 2; done && python manage.py runserver 0.0.0.0:8000"]
