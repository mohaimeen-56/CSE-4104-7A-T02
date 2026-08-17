# CSE4104-7A-T02 — Setup & Deployment Guide

**AI Sales Analytics Dashboard (SalesIQ)**

This guide walks you through setting up and running the project locally, configuring PostgreSQL / Supabase, seeding sample records, and deploying to cloud platforms (Vercel, Render, Supabase).

---

## 1. Local Development Setup

### System Prerequisites
- **Python 3.10+** (Python 3.11 / 3.12 / 3.14 supported)
- **Node.js 18+** and **npm 9+**
- **Git**

---

### 2. Backend Configuration

1. **Navigate to Backend Directory:**
   ```bash
   cd C:\myproject\CSE4104_T2\backend
   ```

2. **Create Python Virtual Environment (Optional but Recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Modify `.env` as needed:
   ```env
   # For local SQLite (Default):
   DATABASE_URL=sqlite:///./sales_dashboard.db

   # For PostgreSQL / Supabase:
   # DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres

   JWT_SECRET=your-secure-secret-key-2026
   AI_PROVIDER=grounded
   GEMINI_API_KEY=
   OPENAI_API_KEY=
   ```

5. **Run Database Seeding:**
   ```bash
   python seed.py
   ```
   This will initialize all tables, constraints, indexes, and populate 345+ sales records spanning Jan-Aug 2026 with 4 demo accounts.

6. **Start FastAPI Backend Server:**
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```
   Test API availability by visiting `http://127.0.0.1:8000/api/health` or `http://127.0.0.1:8000/docs`.

---

### 3. Frontend Configuration

1. **Navigate to Frontend Directory:**
   ```bash
   cd C:\myproject\CSE4104_T2\frontend
   ```

2. **Install Dependencies:**
   ```bash
   npm install
   ```

3. **Start Vite Development Server:**
   ```bash
   npm run dev
   ```
   Open `http://localhost:5173` in your browser.

4. **Compile Production Build:**
   ```bash
   npm run build
   ```

---

## 4. Supabase Database Deployment

1. Create a project at [supabase.com](https://supabase.com).
2. Go to **Project Settings > Database** and copy the URI connection string.
3. In the Supabase **SQL Editor**, paste and execute `database/schemas.sql`.
4. Set the `DATABASE_URL` in your backend `.env` file to your Supabase PostgreSQL URI:
   ```text
   DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
   ```
5. Run `python backend/seed.py` to seed data into Supabase directly.

---

## 5. Render Backend Deployment

1. Create a new **Web Service** on [render.com](https://render.com).
2. Connect your Git repository.
3. Configure settings:
   - **Environment:** Python 3
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables (`DATABASE_URL`, `JWT_SECRET`, `AI_PROVIDER`, `CORS_ORIGINS`).

---

## 6. Vercel Frontend Deployment

1. Create a project on [vercel.com](https://vercel.com).
2. Set **Root Directory** to `frontend`.
3. Set **Build Command** to `npm run build` and **Output Directory** to `dist`.
4. Add environment variable: `VITE_API_BASE_URL=https://your-render-app.onrender.com/api`.
