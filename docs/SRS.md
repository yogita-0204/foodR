# Software Requirements Specification (SRS)

Project: ShopApp / foodR
Author: Generated
Date: 2026-05-08

## 1. Introduction

- Purpose: This SRS describes functional and non-functional requirements for the ShopApp (foodR) project: a Django-based platform for college users to order food from nearby shop owners, and for shop owners to manage menus and orders.
- Scope: Web application with user accounts, shop owner accounts, menu management, ordering, payments integration, notifications, and an admin panel.

## 2. Overall Description

- Users: College users (students/staff) and Shop owners.
- Major features:
  - Registration and login for both user types
  - Role-based dashboard and access control
  - Shop and menu management for owners
  - Browsing and ordering menu items for users
  - Order lifecycle management (placed → preparing → ready → completed/cancelled)
  - Payments integration (payments app)
  - Notifications for order status and admin events
  - Admin panel for managing models and site content

## 3. Functional Requirements

1. FR1 — User registration and authentication
   - Users may register as college users or shop owners.
   - Users authenticate via email (username=email).
2. FR2 — Role-based access
   - `Profile.role` distinguishes `college_user` and `shop_owner`.
   - Shop-owner-only views require the `shop_owner` role.
3. FR3 — Shop management
   - Shop owners create and configure their shops, menus, hours, and capacity.
4. FR4 — Menu & items
   - Menu items have images, price, description, and category.
5. FR5 — Ordering
   - Users add items to cart, checkout, and place orders with pickup time selection.
   - Orders produce notifications and update order status.
6. FR6 — Payments
   - Payment records are stored and linked to orders.
7. FR7 — Notifications
   - Notifications are stored in `Notification` and surfaced in the UI.
8. FR8 — Admin panel
   - Admin (Django admin) manages `Profile`, `Notification`, `Shop`, `MenuItem`, `Order`, and `Payment` models.

## 4. Non-functional Requirements

- NFR1 — Security: Use Django's authentication and CSRF protection; session cookie settings configured in `settings.py`.
- NFR2 — Performance: Support typical college load; caching static files via WhiteNoise in production.
- NFR3 — Maintainability: Modular Django apps (`accounts`, `shops`, `menu`, `orders`, `payments`).
- NFR4 — Portability: Runs on Python 3.13+ and Django 5.x.
- NFR5 — Data retention: Keep order and payment history; notifications expire by business rule.

## 5. System Architecture

High-level architecture (Mermaid):

```mermaid
graph LR
  A[Browser / Client] -->|HTTPS| B(Web Server - Django)
  B --> C[Django apps]
  C --> D[(SQLite/Postgres DB)]
  C --> E[Payment Provider]
  C --> F[Email Service / Console Backend]
  subgraph Django apps
    A1[accounts]
    A2[shops]
    A3[menu]
    A4[orders]
    A5[payments]
    A6[admin]
  end
  B -->|Static files| G[WhiteNoise/CDN]
```

Notes: The web server runs the Django application, which routes requests to app-level views. Persistent storage is a relational DB (sqlite for development; Postgres recommended for production). Payment provider is an external service.

## 6. Component / Low-level Diagram

Component interactions and responsibilities (Mermaid):

```mermaid
classDiagram
    class accounts {
      +register()
      +login()
      +profile()
    }
    class shops {
      +create_shop()
      +manage_hours()
      +owner_dashboard()
    }
    class menu {
      +add_item()
      +upload_image()
      +list_items()
    }
    class orders {
      +cart()
      +checkout()
      +update_status()
    }
    class payments {
      +create_payment()
      +verify_payment()
    }
    class notifications {
      +create_notification()
      +mark_read()
    }

    accounts --> orders : "place order / user info"
    shops --> menu : "manage menu"
    menu --> orders : "menu item details"
    orders --> payments : "initiate payment"
    payments --> orders : "payment result"
    orders --> notifications : "order status updates"
    accounts --> notifications : "user notifications"

```

## 7. Database ER Diagram

ER diagram (Mermaid ER):

```mermaid
erDiagram
    AUTH_USER {
        int id PK
        string username
        string email
        string password
        bool is_staff
        bool is_active
    }

    PROFILE {
        int id PK
        int user_id FK
        string role
        string college_id
        string phone_number
        datetime created_at
    }

    SHOP {
        int id PK
        int owner_id FK
        string name
        text description
        string phone
        string email
        time opening_time
        time closing_time
        int max_orders_per_slot
    }

    MENU_ITEM {
        int id PK
        int shop_id FK
        string name
        text description
        decimal price
        bool available
    }

    MENU_ITEM_IMAGE {
        int id PK
        int menu_item_id FK
        string image_path
    }

    ORDER {
        int id PK
        int user_id FK
        int shop_id FK
        datetime placed_at
        string status
        decimal total_amount
        datetime pickup_time
    }

    ORDER_ITEM {
        int id PK
        int order_id FK
        int menu_item_id FK
        int quantity
        decimal unit_price
    }

    PAYMENT {
        int id PK
        int order_id FK
        string provider
        string provider_payment_id
        string status
        decimal amount
        datetime created_at
    }

    NOTIFICATION {
        int id PK
        int user_id FK
        string type
        string title
        text message
        bool is_read
        datetime created_at
    }

    AUTH_USER ||--o{ PROFILE : has
    AUTH_USER ||--o{ ORDER : places
    AUTH_USER ||--o{ NOTIFICATION : receives
    PROFILE }o--|| SHOP : owns
    SHOP ||--o{ MENU_ITEM : has
    MENU_ITEM ||--o{ MENU_ITEM_IMAGE : has
    SHOP ||--o{ ORDER : receives
    ORDER ||--o{ ORDER_ITEM : contains
    ORDER ||--o{ PAYMENT : paid_by
    MENU_ITEM ||--o{ ORDER_ITEM : referenced_in

```

## 8. Data Dictionary (key fields)

- `AUTH_USER.username` — Email used as username.
- `PROFILE.role` — Enum: `college_user` or `shop_owner`.
- `SHOP.max_orders_per_slot` — Limit used in scheduling pickup windows.
- `MENU_ITEM.price` — Decimal currency value.
- `ORDER.status` — Enum: `placed`, `preparing`, `ready`, `completed`, `cancelled`.
- `PAYMENT.status` — Enum: `pending`, `success`, `failed`, `refunded`.

## 9. Use Cases (brief)

- UC1: Register & Login (User)
- UC2: Register Shop Owner & Create Shop
- UC3: Browse Shops & Menu
- UC4: Add to Cart & Checkout
- UC5: Shop Owner Accepts & Prepares Order
- UC6: User Picks up Order & Confirms Completion

## 10. Constraints & Assumptions

- Assumes external payment provider integration for real payments.
- Development uses SQLite; production should use Postgres or MySQL.
- Static files served by WhiteNoise in simple deployments; use CDN behind production.

## 11. Admin & Authorization Notes

- Django Admin (`/admin/`) is enabled and `accounts.admin` registers `Profile` and `Notification`.
- Admin access requires a superuser with `is_staff=True` and `is_superuser=True` as per Django.
- Role-based view access is enforced at view level by checking `Profile.role` or decorators.

## 12. Deployment Recommendations

- Use Postgres, configure `ALLOWED_HOSTS`, and set `DEBUG=False`.
- Configure real email backend and secure environment variables for `SECRET_KEY`.
- Use Gunicorn / Daphne behind Nginx for production; enable HTTPS and HSTS.

---

If you want, I can also:
- export the diagrams as PNG/SVG files,
- move `SRS.md` to a different folder, or
- generate PlantUML versions of the diagrams.
