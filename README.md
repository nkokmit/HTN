# BookStore Microservices - Assignment 05

This workspace contains a Django REST Framework microservice decomposition with 12 services:

1. staff-service
2. manager-service
3. customer-service
4. catalog-service
5. book-service
6. cart-service
7. order-service
8. ship-service
9. pay-service
10. comment-rate-service
11. recommender-ai-service
12. api-gateway

## Implemented Functional Flows

- Customer registration auto-creates cart: `customer-service` calls `cart-service` on `POST /customers/`.
- Staff manages books: `staff-service` calls `book-service` on `POST /staff/books/`.
- Customer cart actions: add, view, update via `cart-service` endpoints.
- Order triggers payment and shipping: `order-service` calls `pay-service` and `ship-service`.
- Customer rates books: `comment-rate-service` provides rating APIs.

## Database Requirement

- SQLite was removed from service configurations.
- Every service uses PostgreSQL via environment variables.
- Docker Compose provisions an independent Postgres container per service.

## Run

```bash
docker compose up --build
```

Gateway runs at `http://localhost:8080`.

## Documentation

- Architecture diagrams: `docs/architecture-diagrams.md`
- API documentation: `docs/api-documentation.md`

## Main Internal Service Endpoints

- book-service: `GET/POST /books/`, `GET/PATCH /books/<id>/`
- customer-service: `GET/POST /customers/`
- cart-service: `POST /carts/`, `POST /cart-items/`, `PATCH /cart-items/<id>/`, `GET /carts/<customer_id>/`
- staff-service: `POST /staff/books/`
- catalog-service: `GET /catalog/books/`
- order-service: `GET/POST /orders/`
- pay-service: `POST /payments/`
- ship-service: `POST /shipments/`
- comment-rate-service: `GET/POST /ratings/`
- recommender-ai-service: `GET /recommendations/`
