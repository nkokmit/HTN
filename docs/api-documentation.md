# API Documentation

Base access for browser/app goes through the gateway:

- UI base: http://localhost:8080
- API gateway prefixes:
  - /book
  - /customer
  - /cart
  - /staff
  - /manager
  - /catalog
  - /order
  - /pay
  - /ship
  - /rating
  - /recommender

## customer-service

### POST /customer/auth/register/
Register new customer. UI registration always uses CUSTOMER role.

Request:
```json
{
  "name": "Nguyen Van A",
  "email": "a@example.com",
  "password": "123456"
}
```

Response 201:
```json
{
  "id": 1,
  "name": "Nguyen Van A",
  "email": "a@example.com",
  "role": "CUSTOMER"
}
```

Behavior:
- Automatically creates cart via cart-service.
- Registration fails if cart creation fails.

### POST /customer/auth/login/
Request:
```json
{
  "email": "a@example.com",
  "password": "123456"
}
```

Response 200:
```json
{
  "token": "demo-token-1",
  "user": {
    "id": 1,
    "name": "Nguyen Van A",
    "email": "a@example.com",
    "role": "CUSTOMER"
  }
}
```

### GET /customer/customers/
List customers.

### POST /customer/customers/
Create customer directly.

## book-service

### GET /book/books/
List books.

Response:
```json
[
  {
    "id": 1,
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "price": "10.50",
    "stock": 20
  }
]
```

### POST /book/books/
Create book.

Request:
```json
{
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "price": "10.50",
  "stock": 20
}
```

### GET /book/books/{book_id}/
Get book detail.

### PATCH /book/books/{book_id}/
Update partial book data.

### PUT /book/books/{book_id}/
Replace book data.

### DELETE /book/books/{book_id}/
Delete book.

## staff-service

### GET /staff/staff/books/
List books through staff-service.

### POST /staff/staff/books/
Create book via staff-service.

Request:
```json
{
  "book": {
    "title": "DDD",
    "author": "Eric Evans",
    "price": "22.00",
    "stock": 18
  },
  "note": "Created by staff"
}
```

### PATCH /staff/staff/books/{book_id}/
Update book via staff-service.

Request:
```json
{
  "stock": 12,
  "note": "Stock update"
}
```

### DELETE /staff/staff/books/{book_id}/
Delete book via staff-service.

## cart-service

### POST /cart/carts/
Create cart.

Request:
```json
{
  "customer_id": 1
}
```

### GET /cart/carts/customer/{customer_id}/
Get cart metadata by customer.

Response:
```json
{
  "id": 1,
  "customer_id": 1
}
```

### GET /cart/carts/{customer_id}/
Get all cart items for the customer.

Response:
```json
[
  {
    "id": 1,
    "cart": 1,
    "book_id": 2,
    "quantity": 3
  }
]
```

### POST /cart/cart-items/
Add book to cart. If the book already exists in the cart, quantity is increased.

Request:
```json
{
  "cart": 1,
  "book_id": 2,
  "quantity": 3
}
```

### PATCH /cart/cart-items/{item_id}/
Update quantity.

Request:
```json
{
  "quantity": 5
}
```

### DELETE /cart/cart-items/{item_id}/
Delete cart item.

## order-service

### GET /order/orders/
List all orders.

### GET /order/orders/?customer_id={customer_id}
List orders for one customer.

### GET /order/orders/{order_id}/
Get one order detail including order items.

Response:
```json
{
  "id": 7,
  "customer_id": 3,
  "total_amount": "21.00",
  "pay_method": "COD",
  "ship_method": "FAST",
  "status": "PAYMENT_AND_SHIPPING_CREATED",
  "items": [
    {
      "id": 1,
      "order": 7,
      "cart_item_id": 10,
      "book_id": 1,
      "title": "Clean Code",
      "unit_price": "10.50",
      "quantity": 2,
      "subtotal": "21.00"
    }
  ]
}
```

### POST /order/orders/
Create order and trigger payment + shipping.

Request:
```json
{
  "customer_id": 3,
  "total_amount": "21.00",
  "pay_method": "COD",
  "ship_method": "FAST",
  "order_items": [
    {
      "cart_item_id": 10,
      "book_id": 1,
      "title": "Clean Code",
      "unit_price": "10.50",
      "quantity": 2,
      "subtotal": "21.00"
    }
  ]
}
```

Response 201:
```json
{
  "order": {
    "id": 7,
    "customer_id": 3,
    "total_amount": "21.00",
    "pay_method": "COD",
    "ship_method": "FAST",
    "status": "PAYMENT_AND_SHIPPING_CREATED",
    "items": [
      {
        "id": 1,
        "order": 7,
        "cart_item_id": 10,
        "book_id": 1,
        "title": "Clean Code",
        "unit_price": "10.50",
        "quantity": 2,
        "subtotal": "21.00"
      }
    ]
  },
  "payment": {
    "id": 1,
    "order_id": 7,
    "method": "COD",
    "amount": "21.00",
    "status": "PAID"
  },
  "shipment": {
    "id": 1,
    "order_id": 7,
    "method": "FAST",
    "status": "CREATED"
  }
}
```

Validation:
- pay_method: COD, CARD, BANK
- ship_method: FAST, STANDARD, EXPRESS

## pay-service

### POST /pay/payments/
Request:
```json
{
  "order_id": 7,
  "method": "COD",
  "amount": "21.00"
}
```

## ship-service

### POST /ship/shipments/
Request:
```json
{
  "order_id": 7,
  "method": "FAST"
}
```

## comment-rate-service

### GET /rating/ratings/
List ratings.

### POST /rating/ratings/
Create rating.

Request:
```json
{
  "customer_id": 3,
  "book_id": 1,
  "score": 5,
  "comment": "Great book"
}
```

Validation:
- score must be integer 1..5
- book must exist

## catalog-service

### GET /catalog/catalog/books/
Read catalog books from book-service.

## manager-service

### GET /manager/manager/notes/
List manager notes.

### POST /manager/manager/notes/
Create manager note.

## recommender-ai-service

### GET /recommender/recommendations/
Returns top recommended books sorted by average score.

## Gateway UI Routes

These are browser routes served by `api-gateway`:

- /
- /books
- /book-{id}
- /login
- /register
- /cart
- /order
- /order-{id}
- /ratings
- /staff-books
