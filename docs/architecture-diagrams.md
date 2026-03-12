# Architecture Diagrams

## System Overview

```mermaid
flowchart LR
    UI[Web UI via api-gateway] --> GW[api-gateway\nNginx + SPA]
    GW --> CUS[customer-service]
    GW --> BOOK[book-service]
    GW --> CART[cart-service]
    GW --> STAFF[staff-service]
    GW --> MAN[manager-service]
    GW --> CAT[catalog-service]
    GW --> ORD[order-service]
    GW --> PAY[pay-service]
    GW --> SHIP[ship-service]
    GW --> RATE[comment-rate-service]
    GW --> REC[recommender-ai-service]

    CUS --> CUSDB[(customer-db)]
    BOOK --> BOOKDB[(book-db)]
    CART --> CARTDB[(cart-db)]
    STAFF --> STAFFDB[(staff-db)]
    MAN --> MANDB[(manager-db)]
    CAT --> CATDB[(catalog-db)]
    ORD --> ORDDB[(order-db)]
    PAY --> PAYDB[(pay-db)]
    SHIP --> SHIPDB[(ship-db)]
    RATE --> RATEDB[(comment-rate-db)]
    REC --> RECDB[(recommender-ai-db)]

    CUS --> CART
    STAFF --> BOOK
    CAT --> BOOK
    CART --> BOOK
    ORD --> PAY
    ORD --> SHIP
    REC --> BOOK
    REC --> RATE
```

## 1. api-gateway

```mermaid
flowchart TD
    Browser --> Gateway[api-gateway]
    Gateway --> StaticPages[SPA routes\n/login, /books, /cart, /order]
    Gateway --> ProxyAPIs[Proxy to backend APIs]
```

## 2. customer-service

```mermaid
flowchart TD
    Client --> CustomerAPI[customer-service]
    CustomerAPI --> CustomerDB[(customer-db)]
    CustomerAPI --> CartAPI[cart-service\nauto create cart on register]
```

## 3. book-service

```mermaid
flowchart TD
    StaffOrUI[staff-service / UI / catalog] --> BookAPI[book-service]
    BookAPI --> BookDB[(book-db)]
```

## 4. cart-service

```mermaid
flowchart TD
    CustomerUI --> CartAPI[cart-service]
    CartAPI --> CartDB[(cart-db)]
    CartAPI --> BookAPI[book-service\nvalidate book exists]
```

## 5. staff-service

```mermaid
flowchart TD
    StaffUI --> StaffAPI[staff-service]
    StaffAPI --> StaffDB[(staff-db)]
    StaffAPI --> BookAPI[book-service\ncreate/update/delete book]
```

## 6. manager-service

```mermaid
flowchart TD
    ManagerUI --> ManagerAPI[manager-service]
    ManagerAPI --> ManagerDB[(manager-db)]
```

## 7. catalog-service

```mermaid
flowchart TD
    UserUI --> CatalogAPI[catalog-service]
    CatalogAPI --> CatalogDB[(catalog-db)]
    CatalogAPI --> BookAPI[book-service\nread catalog books]
```

## 8. order-service

```mermaid
flowchart TD
    CustomerCheckout --> OrderAPI[order-service]
    OrderAPI --> OrderDB[(order-db)]
    OrderAPI --> PaymentAPI[pay-service]
    OrderAPI --> ShippingAPI[ship-service]
    OrderAPI --> OrderItems[store order detail lines]
```

## 9. pay-service

```mermaid
flowchart TD
    OrderAPI[order-service] --> PayAPI[pay-service]
    PayAPI --> PayDB[(pay-db)]
```

## 10. ship-service

```mermaid
flowchart TD
    OrderAPI[order-service] --> ShipAPI[ship-service]
    ShipAPI --> ShipDB[(ship-db)]
```

## 11. comment-rate-service

```mermaid
flowchart TD
    CustomerUI --> RatingAPI[comment-rate-service]
    RatingAPI --> RatingDB[(comment-rate-db)]
    RatingAPI --> BookAPI[book-service\nvalidate rated book exists]
```

## 12. recommender-ai-service

```mermaid
flowchart TD
    UserUI --> RecommenderAPI[recommender-ai-service]
    RecommenderAPI --> RecommenderDB[(recommender-ai-db)]
    RecommenderAPI --> BookAPI[book-service]
    RecommenderAPI --> RatingAPI[comment-rate-service]
```

## Core Functional Sequences

### Customer Registration Creates Cart

```mermaid
sequenceDiagram
    participant UI
    participant Customer
    participant Cart
    UI->>Customer: POST /auth/register/
    Customer->>Customer: Create customer row
    Customer->>Cart: POST /carts/ { customer_id }
    Cart-->>Customer: cart created
    Customer-->>UI: customer response
```

### Checkout Creates Order, Payment, Shipping

```mermaid
sequenceDiagram
    participant UI
    participant Order
    participant Pay
    participant Ship
    UI->>Order: POST /orders/ + order_items
    Order->>Order: Create order + order item lines
    Order->>Pay: POST /payments/
    Order->>Ship: POST /shipments/
    Pay-->>Order: payment created
    Ship-->>Order: shipment created
    Order-->>UI: order, payment, shipment
```
