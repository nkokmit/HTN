FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY cart_service /app

EXPOSE 8000
CMD ["sh", "-c", "python manage.py makemigrations app && until python manage.py migrate; do echo 'Waiting for cart-db...'; sleep 2; done && python manage.py runserver 0.0.0.0:8000"]
