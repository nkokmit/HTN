# BookStore Microservices - Assignment 05

This workspace contains a microservice decomposition with the following active services:

1. user-service
2. catalog-service
3. cart-service
4. order-service
5. ship-service
6. pay-service
7. comment-rate-service
8. recommender-ai-service
9. api-gateway

## Implemented Functional Flows

- User registration auto-creates cart for `CUSTOMER` role: `user-service` calls `cart-service` on `POST /customers/`.
- Staff/admin manage books and manager notes through `user-service`.
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
Mobile UI is available at `http://localhost:8080/mobile`.

Open the mobile UI route in a browser, then use the buttons and forms to browse books, register a customer, and send ratings.

## Seed Data

After the stack is up, run:

```bash
python seed_data.py
```

The script populates sample data across user, cart, catalog, clothes, order, payment, shipment, rating, and recommendation flows through the gateway.

## Documentation

- Architecture diagrams: `docs/architecture-diagrams.md`
- API documentation: `docs/api-documentation.md`

## Main Internal Service Endpoints

- user-service: `GET/POST /users/`, `GET/POST /customers/`, `POST /auth/register/`, `POST /auth/login/`, `GET/POST /staff/books/`, `GET/POST /manager/notes/`
- cart-service: `POST /carts/`, `POST /cart-items/`, `PATCH /cart-items/<id>/`, `GET /carts/<customer_id>/`
- catalog-service: `GET /catalog/books/`
- order-service: `GET/POST /orders/`
- pay-service: `POST /payments/`
- ship-service: `POST /shipments/`
- comment-rate-service: `GET/POST /ratings/`
- recommender-ai-service: `GET /recommendations/`















































































