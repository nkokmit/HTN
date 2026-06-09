# Architecture Diagrams

## System Overview

```mermaid
flowchart LR
    UI[Mobile UI route\n/mobile] --> GW[api-gateway\nFastAPI + SPA]
    GW --> USER[user-service]
    GW --> BOOK[book-service]
    GW --> CART[cart-service]
    GW --> CAT[catalog-service]
    GW --> ORD[order-service]
    GW --> PAY[pay-service]
    GW --> SHIP[ship-service]
    GW --> RATE[comment-rate-service]
    GW --> REC[recommender-ai-service]

    USER --> USERDB[(user-db)]
    BOOK --> BOOKDB[(book-db)]
    CART --> CARTDB[(cart-db)]
    CAT --> CATDB[(catalog-db)]
    ORD --> ORDDB[(order-db)]
    PAY --> PAYDB[(pay-db)]
    SHIP --> SHIPDB[(ship-db)]
    RATE --> RATEDB[(comment-rate-db)]
    REC --> RECDB[(recommender-ai-db)]

    USER --> CART
    USER --> BOOK
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

## 2. mobile-route

```mermaid
flowchart TD
    PhoneBrowser --> Gateway[api-gateway]
    Gateway --> MobileSPA[Responsive bookstore UI on /mobile]
```

## 3. user-service

```mermaid
flowchart TD
    Client --> UserAPI[user-service]
    UserAPI --> UserDB[(user-db)]
    UserAPI --> CartAPI[cart-service\nauto create cart for CUSTOMER role]
    UserAPI --> StaffAPI[catalog-service\nstaff/admin book management]
    UserAPI --> ManagerAPI[manager notes]
```

## 4. cart-service

```mermaid
flowchart TD
    CustomerUI --> CartAPI[cart-service]
    CartAPI --> CartDB[(cart-db)]
    CartAPI --> BookAPI[catalog-service\nvalidate product exists]
```

## 5. catalog-service

```mermaid
flowchart TD
    UserUI --> CatalogAPI[catalog-service]
    CatalogAPI --> CatalogDB[(catalog-db)]
    CatalogAPI --> ProductAPI[product data]
```

## 9. order-service

```mermaid
flowchart TD
    CustomerCheckout --> OrderAPI[order-service]
    OrderAPI --> OrderDB[(order-db)]
    OrderAPI --> PaymentAPI[pay-service]
    OrderAPI --> ShippingAPI[ship-service]
    OrderAPI --> OrderItems[store order detail lines]
```

## 10. pay-service

```mermaid
flowchart TD
    OrderAPI[order-service] --> PayAPI[pay-service]
    PayAPI --> PayDB[(pay-db)]
```

## 11. ship-service

```mermaid
flowchart TD
    OrderAPI[order-service] --> ShipAPI[ship-service]
    ShipAPI --> ShipDB[(ship-db)]
```

## 12. comment-rate-service

```mermaid
flowchart TD
    CustomerUI --> RatingAPI[comment-rate-service]
    RatingAPI --> RatingDB[(comment-rate-db)]
    RatingAPI --> BookAPI[book-service\nvalidate rated book exists]
```

## 13. recommender-ai-service

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

### PlantUML: Customer Chọn Sách -> Thêm Giỏ -> Thanh Toán

```plantuml
@startuml
title Customer đặt đơn hàng (Order Checkout)

actor Customer as C
participant "Web UI" as UI
participant "api-gateway\n(FastAPI)" as GW
participant "order-service" as ORD
database "order-db" as ORDDB
participant "pay-service" as PAY
database "pay-db" as PAYDB
participant "ship-service" as SHIP
database "ship-db" as SHIPDB

C -> UI: Chọn checkout
UI -> GW: POST /order/orders/\n{customer_id,total_amount,pay_method,ship_method,order_items}
GW -> ORD: Forward POST /orders/

ORD -> ORD: Validate pay_method, ship_method

alt Dữ liệu không hợp lệ
  ORD --> GW: 400 Bad Request
  GW --> UI: 400 + validation errors
  UI --> C: Hiển thị lỗi
else Hợp lệ
  ORD -> ORDDB: INSERT Order(status=CREATED)
  ORDDB --> ORD: order_id
  loop Với mỗi phần tử trong order_items
    ORD -> ORDDB: INSERT OrderItem(...)
  end

  ORD -> PAY: POST /payments/\n{order_id, method, amount}
  PAY -> PAYDB: INSERT Payment(status=PAID)
  PAYDB --> PAY: payment_id
  PAY --> ORD: 201 payment

  ORD -> SHIP: POST /shipments/\n{order_id, method}
  SHIP -> SHIPDB: INSERT Shipment(status=CREATED)
  SHIPDB --> SHIP: shipment_id
  SHIP --> ORD: 201 shipment

  alt Pay và Ship đều thành công (200/201)
    ORD -> ORDDB: UPDATE Order.status=PAYMENT_AND_SHIPPING_CREATED
    ORD --> GW: 201 {order,payment,shipment}
  else Một trong hai thất bại
    ORD -> ORDDB: UPDATE Order.status=PARTIAL_FAILED
    ORD --> GW: 201 {order,payment?,shipment?}
  end

  GW --> UI: Response checkout
  UI --> C: Hiển thị kết quả đơn hàng
end

opt Pay/Ship service unavailable (timeout/network)
  ORD -> ORDDB: UPDATE Order.status=DEPENDENCY_UNAVAILABLE
  ORD --> GW: 502 {error, order}
  GW --> UI: 502 Bad Gateway
  UI --> C: Báo lỗi phụ thuộc dịch vụ
end

@enduml