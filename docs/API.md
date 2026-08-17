# CSE4104-7A-T02 — REST API Documentation

**AI Sales Analytics Dashboard (SalesIQ)**

All API endpoints are prefixed with `/api`. Interactive Swagger documentation is available at `http://127.0.0.1:8000/docs`.

---

## 1. Authentication & Users

### `POST /api/auth/register`
Create a new user account.
- **Request Body:**
  ```json
  {
    "name": "Afia Maliha Priota",
    "email": "priota@example.com",
    "password": "viewerpassword123",
    "role": "viewer"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "success": true,
    "message": "Registration successful",
    "data": {
      "access_token": "eyJhbGciOi...",
      "token_type": "bearer",
      "user": {
        "id": 4,
        "name": "Afia Maliha Priota",
        "email": "priota@example.com",
        "role": "viewer"
      }
    }
  }
  ```

### `POST /api/auth/login`
Authenticate with email and password to receive a JWT access token.
- **Request Body:**
  ```json
  {
    "email": "pial@example.com",
    "password": "admin123"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "success": true,
    "message": "Login successful",
    "data": {
      "access_token": "eyJhbGciOi...",
      "token_type": "bearer",
      "user": {
        "id": 1,
        "name": "Mohaimeen Islam Pial",
        "email": "pial@example.com",
        "role": "admin"
      }
    }
  }
  ```

### `GET /api/auth/me`
Retrieve profile of currently authenticated user.
- **Headers:** `Authorization: Bearer <token>`
- **Response (200 OK):** User object.

### `PUT /api/users/me`
Update profile name and optionally change password.
- **Headers:** `Authorization: Bearer <token>`
- **Request Body:**
  ```json
  {
    "name": "Mohaimeen Islam Pial",
    "password": "newpassword123",
    "current_password": "admin123"
  }
  ```

---

## 2. Sales Operations

### `GET /api/sales`
List sales records with server-side pagination, search, and multi-field filters.
- **Query Parameters:**
  - `page` (int, default: 1)
  - `page_size` (int, default: 10)
  - `search` (string, optional)
  - `region_id` (int, optional)
  - `product_id` (int, optional)
  - `category` (string, optional)
  - `start_date` (YYYY-MM-DD, optional)
  - `end_date` (YYYY-MM-DD, optional)
  - `sort_by` (string, default: "sale_date")
  - `sort_order` (string: "asc" or "desc", default: "desc")
- **Response (200 OK):**
  ```json
  {
    "success": true,
    "message": "Sales records retrieved",
    "data": [
      {
        "id": 1,
        "quantity": 4,
        "unit_price": 87500.00,
        "total_price": 350000.00,
        "sale_date": "2026-05-14",
        "product": { "id": 1, "name": "iPhone 15", "category": "Phone" },
        "region": { "id": 1, "name": "Dhaka", "country": "Bangladesh" }
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 10,
      "total": 345,
      "total_pages": 35
    }
  }
  ```

### `POST /api/sales`
Create a new sales record *(Admin / Manager)*.
- **Request Body:**
  ```json
  {
    "product_id": 1,
    "region_id": 1,
    "quantity": 5,
    "unit_price": 87500.00,
    "sale_date": "2026-08-16"
  }
  ```

### `PUT /api/sales/{id}`
Update an existing sales record *(Admin / Manager)*.

### `DELETE /api/sales/{id}`
Delete a sales record *(Admin only)*.

### `POST /api/sales/upload-csv`
Bulk import sales records via multipart CSV file *(Admin / Manager)*.
- **Request:** `file` (multipart/form-data CSV file)
- **Response (200 OK):**
  ```json
  {
    "success": true,
    "message": "CSV processing complete: 50 rows imported, 0 rows failed.",
    "data": {
      "total_rows": 50,
      "imported_rows": 50,
      "failed_rows": 0,
      "errors": []
    }
  }
  ```

---

## 3. Analytics Endpoints

- `GET /api/analytics/overview`: Complete dashboard payload (KPIs, trend, product/category/region breakdown, top products).
- `GET /api/analytics/summary`: Summary KPI numbers and growth deltas.
- `GET /api/analytics/revenue-trend`: Monthly or daily time-series revenue aggregates.
- `GET /api/analytics/by-product`: Revenue and units sold per product.
- `GET /api/analytics/by-category`: Revenue and percentage share per category.
- `GET /api/analytics/by-region`: Revenue and percentage share per region.
- `GET /api/analytics/top-products`: Ranked top selling products.

---

## 4. AI & Machine Learning Endpoints

### `POST /api/ai/insights`
Generate executive business intelligence insights for a time period.
- **Request Body:**
  ```json
  {
    "period": "this_month"
  }
  ```

### `GET /api/ai/forecast`
Compute next-month revenue projection using scikit-learn Linear Regression.

### `GET /api/ai/anomalies`
Detect statistical sales spikes, drops, and low inventory levels.

### `POST /api/ai/chat`
Ask natural language questions about business performance.
- **Request Body:**
  ```json
  {
    "message": "Which product had the best sales in March?"
  }
  ```

---

## 5. Reports & Exports

- `GET /api/reports/monthly`: Aggregated monthly intelligence report data.
- `GET /api/reports/export/csv`: Download full sales records CSV file.
- `GET /api/reports/export/pdf`: Download formal ReportLab executive PDF report.

---

## 6. Notifications

- `GET /api/notifications`: Retrieve current user notifications.
- `GET /api/notifications/unread-count`: Get unread badge count.
- `PUT /api/notifications/{id}/read`: Mark notification as read.
- `PUT /api/notifications/read-all`: Mark all notifications as read.
