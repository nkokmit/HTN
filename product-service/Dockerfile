FROM python:3.12-slim

ARG PIP_INDEX_URL=https://pypi.org/simple
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt /app/requirements.txt
# Increase pip timeout and allow overriding index via build-arg to avoid intermittent ReadTimeouts
RUN pip --default-timeout=120 install --no-cache-dir -r /app/requirements.txt -i $PIP_INDEX_URL
COPY product_service /app

EXPOSE 8000
CMD ["sh", "-c", "python manage.py migrate --noinput ; python manage.py runserver 0.0.0.0:8000"]
