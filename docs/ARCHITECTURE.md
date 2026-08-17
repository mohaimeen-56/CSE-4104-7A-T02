# CSE4104-7A-T02 — System Architecture & Security Specification

**AI Sales Analytics Dashboard (SalesIQ)**

---

## 1. High-Level 4-Layer Architecture

```text
┌────────────────────────────────────────────────────────┐
│                   1. CLIENT LAYER                      │
│   React 18 + Tailwind CSS + Recharts + React Router    │
│   Axios Client (Bearer Token Interceptor)              │
└───────────────────────────┬────────────────────────────┘
                            │ HTTPS / JSON REST APIs
┌───────────────────────────▼────────────────────────────┐
│                  2. BACKEND LAYER                      │
│   FastAPI + Pydantic v2 + Dependency Injection         │
│   Auth & RBAC (PyJWT + bcrypt)                         │
│   Services: Sales, Analytics, CSV Parser, ReportLab    │
└─────────────┬────────────────────────────┬─────────────┘
              │                            │
┌─────────────▼──────────────┐ ┌───────────▼─────────────┐
│     3. DATABASE LAYER      │ │   4. AI & ML SERVICES   │
│ PostgreSQL / Supabase      │ │ Scikit-Learn Forecaster │
│ (SQLAlchemy ORM + Indexes) │ │ Statistical Anomaly Det.│
│ users, products, regions,  │ │ Grounded Synthesis Eng. │
│ sales, ai_logs, notifs     │ │ Google Gemini / OpenAI  │
└────────────────────────────┘ └─────────────────────────┘
```

---

## 2. Security & Role-Based Access Control (RBAC)

### Password Hashing
All user passwords are encrypted using `bcrypt` (12 rounds). Plaintext passwords are never saved to disk or transmitted across unauthorized boundaries.

### JWT Token Protocol
- Tokens are signed with HMAC-SHA256 (`HS256`) using a server-side `JWT_SECRET`.
- Payload includes `sub` (User ID), `role` (`admin`, `manager`, `viewer`), and `exp` (timestamp expiration).
- Backend dependencies (`get_current_user`, `require_admin`, `require_manager_or_admin`) intercept every protected route to enforce access control. Frontend role claims are never trusted blindly.

### Role Permission Matrix

| Capability | Admin | Manager | Viewer |
|---|---|---|---|
| View Dashboard & Charts | ✅ | ✅ | ✅ |
| Filter & Search Sales | ✅ | ✅ | ✅ |
| Create Sales Records | ✅ | ✅ | ❌ |
| Edit Sales Records | ✅ | ✅ | ❌ |
| Delete Sales Records | ✅ | ❌ | ❌ |
| Bulk CSV Upload | ✅ | ✅ | ❌ |
| Generate AI Insights | ✅ | ✅ | ✅ |
| Query AI Chatbot | ✅ | ✅ | ✅ |
| Export PDF & CSV Reports | ✅ | ✅ | ✅ |
| Manage User Roles | ✅ | ❌ | ❌ |

---

## 3. Machine Learning & AI Design

### Revenue Forecasting (`ml/forecaster.py`)
- Historical monthly revenue time-series aggregates are extracted via SQL.
- A Ordinary Least Squares (OLS) / Ridge regression model from `scikit-learn` is fitted to time indices.
- Projections for subsequent months are computed alongside standard residual error bounds (95% confidence interval).
- Gracefully handles insufficient data (< 2 months) with informative baseline fallback.

### Anomaly Detection (`ml/anomaly_detector.py`)
- Employs a rolling z-score statistical deviation metric:
  $$z = \frac{x - \mu}{\sigma}$$
- Deviations exceeding \(z > 1.8\) are flagged as positive spikes, while \(z < -1.8\) flags acute regional drops.
- Inventory levels below 20 units generate automated low-stock flags across warehouses.

### Natural Language Sales Chatbot (`ai/chatbot.py`)
1. Ingests user query.
2. Identifies intent (best product, region performance, total revenue, fast growing category, worst region).
3. Executes safe, parameterized ORM aggregations against PostgreSQL.
4. Generates structured responses formatted with bold markdown and currency amounts (৳).
5. Automatically archives interaction to the `ai_logs` table.
