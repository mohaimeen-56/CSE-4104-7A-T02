# CSE4104-7A-T02 — AI Sales Analytics Dashboard

**An Intelligent, Data-Driven Business Intelligence System**

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React_18-61DAFB.svg)](https://react.dev)
[![Tailwind CSS](https://img.shields.io/badge/Styles-Tailwind_CSS-38B2AC.svg)](https://tailwindcss.com)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL_/_Supabase-336791.svg)](https://supabase.com)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-F7931E.svg)](https://scikit-learn.org)

---

## 1. Project Overview

The **AI Sales Analytics Dashboard (SalesIQ)** is a production-grade full-stack web application that transforms raw business sales transactions into real-time interactive business intelligence, next-month revenue forecasting, automatic statistical anomaly detection, actionable business recommendations, PDF/CSV report generation, and natural language sales inquiries via an intelligent AI chatbot.

---

## 2. Team Information

- **Course:** CSE4104 — Web Engineering Lab
- **Section:** 7A
- **Team Name:** CSE4104-7A-T02
- **Institution:** Northern University of Business and Technology, Khulna

| Role | Name | Student ID |
|---|---|---|
| **Team Leader** | Mohaimeen Islam Pial | 11230121094 |
| **Frontend Developer** | Sk Mesbaul Arefin | 11230121077 |
| **Backend Developer** | Sumaiya Akter | 11230121081 |
| **Database Manager** | Afia Maliha Priota | 11230121090 |

---

## 3. Technology Stack

### Frontend
- **Framework:** React.js (Vite)
- **Styling:** Tailwind CSS (Approved color tokens `#1F3864` Primary Navy, `#2E86AB` Secondary Teal)
- **Visualizations:** Recharts (Area charts, Bar charts, Donut charts)
- **Icons:** Lucide React
- **Routing:** React Router v6 (Protected routes & Role-Based Access Control)
- **HTTP Client:** Axios (Centralized client with automatic JWT token interceptor)

### Backend
- **Framework:** Python FastAPI
- **Data Processing:** pandas & numpy
- **Machine Learning:** scikit-learn (Linear Regression revenue forecaster & statistical anomaly detector)
- **ORM & Database:** SQLAlchemy with PostgreSQL (Supabase) and SQLite local fallback
- **Authentication & Security:** JWT (PyJWT), bcrypt password hashing, Role-Based Access Control (RBAC)
- **Report Generation:** ReportLab (Formal PDF generation) & CSV export engine

### AI & LLM Service Layer
- Pluggable AI Provider Interface (`AIProvider`) supporting:
  - **Google Gemini API** (`gemini-1.5-flash`)
  - **OpenAI API** (`gpt-4o-mini`)
  - **Grounded Heuristic Synthesis Engine** (100% data-grounded fallback ensuring offline reliability and zero hallucinations)

---

## 4. Key Features & Capabilities

1. **Authentication & User Management:**
   - Secure registration, login, logout, and profile management with bcrypt password hashing.
   - Role-Based Access Control: **Admin**, **Manager**, and **Viewer**.
2. **Sales Data Management:**
   - Server-side paginated sales table with multi-criteria filtering (Region, Category, Date range) and free-text search.
   - Add, edit, and delete sales records with role permission enforcement.
3. **Bulk CSV Import:**
   - Drag-and-drop CSV upload with row-by-row validation (`product_id`, `region_id`, `quantity`, `unit_price`, `sale_date`) and comprehensive error reporting.
4. **Interactive Dashboard & Visualizations:**
   - Summary KPI cards: Total Revenue, Total Completed Orders, Average Order Value (with month-over-month % deltas).
   - Revenue trend line/area chart, product distribution bar chart, regional sales donut chart, and top performing products ranked table.
5. **AI Insights Generator:**
   - Period-filtered executive business intelligence narratives analyzing revenue drivers, top products, and basket dynamics.
6. **AI Sales Forecaster (Machine Learning):**
   - Scikit-learn Linear Regression trained on historical monthly revenue to predict next-month revenue trajectory and confidence bounds.
7. **AI Anomaly Detector:**
   - Statistical z-score and rolling IQR anomaly detector flagging abnormal sales spikes, drops, and low inventory levels (< 20 units).
8. **AI Natural Language Sales Chatbot:**
   - Conversational query interface translating natural questions into safe parameterized database queries and natural language answers.
9. **Reports & Exports:**
   - One-click formal PDF executive report generation via ReportLab.
   - Real-time CSV sales records and analytics data export.
10. **Notification Center:**
    - Live database-backed alerts for low stock and sales milestones with unread counters.

---

## 5. Demo Accounts

The database comes pre-seeded with 4 demo accounts (passwords generated with standard bcrypt):

| Role | Email | Password | Permissions |
|---|---|---|---|
| **Admin** | `pial@example.com` | `admin123` | Full access: CRUD sales, delete, CSV upload, users, AI |
| **Manager** | `mesbaul@example.com` | `manager123` | Manage sales, CSV upload, analytics, AI, reports |
| **Manager** | `sumaiya@example.com` | `manager123` | Manage sales, CSV upload, analytics, AI, reports |
| **Viewer** | `priota@example.com` | `viewer123` | Read-only access to dashboard, records, AI, and reports |

---

## 6. Quick Start & Local Execution

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### Step 1: Database Setup & Seeding
```bash
# From repository root:
python backend/seed.py
```

### Step 2: Start Backend Server
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```
Backend API will be running at: `http://127.0.0.1:8000` (Swagger docs at `/docs`).

### Step 3: Start Frontend Application
```bash
cd frontend
npm run dev
```
Frontend application will be accessible at: `http://localhost:5173`.

### Step 4: Run Automated Tests
```bash
python -m pytest backend/tests
```

---

## 7. Project Structure

```text
CSE4104_T2/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routers (auth, sales, analytics, ai, reports, notifs, health)
│   │   ├── core/         # Config, security (bcrypt & JWT), dependencies & RBAC
│   │   ├── db/           # Session engine & declarative Base
│   │   ├── models/       # SQLAlchemy models (User, Product, Region, Sale, AILog, Notification)
│   │   ├── schemas/      # Pydantic v2 validation models
│   │   ├── services/     # Business logic & services
│   │   ├── ml/           # Scikit-learn forecaster & anomaly detector
│   │   ├── ai/           # Pluggable AI providers & Chatbot
│   │   └── main.py       # FastAPI application entrypoint
│   ├── tests/            # Pytest test suite
│   ├── requirements.txt  # Python dependencies
│   ├── seed.py           # Database seeding script
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/   # Modular UI components (Charts, Cards, Modals, Chat, Tables)
│   │   ├── context/      # AuthContext & NotificationContext
│   │   ├── layouts/      # AppShell, Sidebar, TopNavbar
│   │   ├── pages/        # Dashboard, SalesRecords, CsvUpload, AIInsights, Chatbot, Reports, Settings
│   │   ├── services/     # Centralized Axios client & API endpoints
│   │   ├── utils/        # Formatters (Currency ৳, Dates, Compact numbers)
│   │   ├── App.jsx       # Route definitions & protected route guards
│   │   └── main.jsx      # React entrypoint
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
├── database/
│   ├── schemas.sql       # PostgreSQL (Supabase) schema definition
│   └── seed.sql          # Seed SQL script
├── docs/
│   ├── API.md            # REST API documentation
│   ├── SETUP.md          # Setup & deployment guide
│   └── ARCHITECTURE.md   # Architectural design specification
└── README.md
```
