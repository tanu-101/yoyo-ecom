# 🔄 System Workflows

## 🛒 Checkout & Payment Workflow (Stripe Webhook)
This workflow ensures that orders are only activated after verified payment confirmation.

```mermaid
sequenceDiagram
    participant Customer
    participant Frontend
    participant Backend
    participant Stripe
    participant DB

    Customer->>Frontend: Click "Place Order"
    Frontend->>Backend: POST /api/orders/
    Backend->>DB: Create Order (Status: Pending Payment)
    Backend->>DB: Lock Inventory (select_for_update)
    Backend->>Stripe: Create PaymentIntent
    Stripe-->>Backend: Client Secret
    Backend-->>Frontend: Client Secret + Order ID
    Frontend->>Stripe: Process Payment (Card details)
    Stripe-->>Frontend: Payment Success
    Frontend->>Customer: Show "Processing..."
    
    Note over Stripe,Backend: Asynchronous Webhook
    Stripe->>Backend: POST /api/webhooks/ (payment_intent.succeeded)
    Backend->>Backend: Verify Webhook Signature
    Backend->>DB: Update Order Status -> "Placed"
    Backend->>DB: Create Payment Record
    Backend-->>Stripe: 200 OK
```

---

## 🔒 Inventory Concurrency Control
Ensures zero overselling by using row-level database locking during checkout.

```mermaid
sequenceDiagram
    participant API
    participant Service
    participant DB

    API->>Service: reserve_stock(variant_id, quantity)
    Service->>DB: BEGIN TRANSACTION
    Service->>DB: SELECT * FROM variant WHERE id = X FOR UPDATE
    Note right of DB: Row is locked for other transactions
    DB-->>Service: Current Stock: 5
    Alt Stock >= Quantity
        Service->>DB: UPDATE variant SET stock = stock - quantity
        Service->>DB: COMMIT
        Service-->>API: Success
    Else Insufficient Stock
        Service->>DB: ROLLBACK
        Service-->>API: Error (OutOfStock)
    End
```

---

## 📦 Order Lifecycle State Machine
Status transitions are restricted to forward-only movements to maintain data integrity.

```mermaid
graph LR
    P[Pending Payment] -->|Payment Success| PL[Placed]
    P -->|Timeout/Cancel| C[Cancelled]
    PL -->|Admin Processing| PR[Processing]
    PR -->|Courier Pick-up| S[Shipped]
    S -->|Delivered| D[Delivered]
    D -->|Customer Request| R[Return Requested]
    R -->|Admin Approve| REF[Refunded/Replaced]
    R -->|Admin Reject| D
    PL -->|Admin/Customer Cancel| C
```

---

## 🔁 Return & Refund Workflow
Handles the complexity of physical returns and stock restoration.

```mermaid
sequenceDiagram
    participant Customer
    participant Admin
    participant System
    participant DB

    Customer->>System: Submit Return Request (Reason + Photos)
    System->>System: Validate Return Window (7 days)
    System->>Admin: Notify: New Return Request
    Admin->>System: Review and Approve Request
    System->>Customer: Email: Return Label & Instructions
    Note over Customer,Admin: Physical Item Returns to Warehouse
    Admin->>System: Mark Item as "Received & Inspected"
    System->>System: Initiate Refund via Stripe
    System->>DB: Update Order Item Status -> "Returned"
    System->>DB: Restore Stock (Optional - based on condition)
    System-->>Customer: Notification: Refund Processed
```

---

**Related Documents:**
- [Orders & Checkout](./04-ORDERS-CHECKOUT.md)
- [Payments & Shipping](./05-PAYMENTS-SHIPPING.md)
- [Database Schema](./09-DATABASE.md)
