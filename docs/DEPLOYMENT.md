# SalesIQ — Production Deployment Guide

**CSE4104-7A-T02 | Northern University of Business and Technology, Khulna**

---

## Active Production Architecture

```
Browser
  │
  ▼
Cloudflare Pages (React Frontend SPA)
  │ HTTPS REST
  ▼
Vercel (FastAPI Python Backend / Serverless)
  ├──► Supabase (PostgreSQL Database)
  └──► Google Gemini API (AI Service)
```

**Alternative Platforms:** Render / Railway for Backend · Netlify / Vercel for Frontend

---

## Environment Variable Matrix

| Variable | Backend (Vercel) | Frontend (Cloudflare) | Type |
|---|---|---|---|
| `DATABASE_URL` | ✅ Required | ❌ Never | SECRET |
| `JWT_SECRET` | ✅ Required | ❌ Never | SECRET |
| `AI_PROVIDER` | ✅ Required (`gemini`) | ❌ Never | config |
| `GEMINI_API_KEY` | ✅ Required | ❌ Never | SECRET |
| `GEMINI_MODEL` | ✅ Required (`gemini-3.5-flash-lite`) | ❌ Never | config |
| `CORS_ORIGINS` | ✅ Required (Cloudflare URL) | ❌ Never | config |
| `ENVIRONMENT` | ✅ `production` | ❌ Never | config |
| `LOG_LEVEL` | ✅ `INFO` | ❌ Never | config |
| `VITE_API_BASE_URL` | ❌ Never | ✅ Required (Vercel URL) | PUBLIC |

> `VITE_*` variables are bundled into the browser JavaScript. **Never put database secrets or API keys in them.**

---

## Step 1 — Supabase Database

1. Go to **[supabase.com](https://supabase.com)** → Create New Project (e.g. `salesiq`).
2. Set a strong database password and choose your nearest region.
3. Wait for database provisioning (~2 minutes).
4. Go to **Project Settings → Database → Connection String** (URI format):
   ```text
   postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-REF].supabase.co:5432/postgres
   ```
5. Append `?sslmode=require` to the end:
   ```text
   postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-REF].supabase.co:5432/postgres?sslmode=require
   ```
   Save this — it becomes `DATABASE_URL` in Vercel.

### Initialize Tables and Seed Initial Data

Run migrations or seed directly against Supabase from your local terminal:

```bash
cd backend
set DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres?sslmode=require
python seed.py
```
*(On Linux/macOS use `export DATABASE_URL=...`)*

---

## Step 2 — Vercel Backend (FastAPI Serverless)

The repository includes `api/index.py` and `vercel.json` configured for Vercel Python Serverless deployment.

1. Go to **[vercel.com](https://vercel.com)** → **Add New... → Project**.
2. Select your repository `CSE-4104-7A-T02`.
3. **Configure Project:**
   - **Framework Preset:** Other
   - **Root Directory:** `./` (Repository root — `vercel.json` and `api/index.py` are at the root)
4. Under **Environment Variables**, add:

   | Key | Value |
   |---|---|
   | `DATABASE_URL` | `postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres?sslmode=require` |
   | `JWT_SECRET` | *(64-character random hex string)* |
   | `AI_PROVIDER` | `gemini` |
   | `GEMINI_API_KEY` | *(Google AI Studio key)* |
   | `GEMINI_MODEL` | `gemini-3.5-flash-lite` |
   | `CORS_ORIGINS` | `*` *(or your Cloudflare Pages domain once known)* |
   | `ENVIRONMENT` | `production` |
   | `LOG_LEVEL` | `INFO` |

5. Click **Deploy**.
6. Note your Vercel Backend URL: `https://your-backend.vercel.app`.
7. Verify health:
   ```text
   https://your-backend.vercel.app/api/health
   ```
   Expected JSON response:
   ```json
   {
     "status": "healthy",
     "database": "healthy",
     "ai_provider": "gemini",
     "ai_configured": true
   }
   ```

---

## Step 3 — Cloudflare Pages Frontend

1. Go to **[dash.cloudflare.com](https://dash.cloudflare.com)** → **Workers & Pages** → **Create application** → **Pages** → **Connect to Git**.
2. Select repository `CSE-4104-7A-T02`.
3. **Build settings:**
   - **Framework Preset:** `Vite`
   - **Root directory:** `frontend`
   - **Build command:** `npm run build`
   - **Build output directory:** `dist`
4. Under **Environment Variables (Production)**, add:
   
   | Variable | Value |
   |---|---|
   | `VITE_API_BASE_URL` | `https://your-backend.vercel.app` |

   *(No trailing slash. The frontend client automatically appends `/api`.)*

5. Click **Save and Deploy**.
6. Cloudflare provides your domain: `https://cse-4104-7a-t02.pages.dev` (or custom domain).

### Update CORS in Vercel Backend
Once you have your Cloudflare URL:
1. Go to **Vercel → Project Settings → Environment Variables**.
2. Set `CORS_ORIGINS`:
   ```text
   https://cse-4104-7a-t02.pages.dev
   ```
3. Redeploy the latest commit on Vercel.

---

## Step 4 — Alternative: Deploy Frontend via Wrangler CLI

If deploying via Cloudflare Wrangler command line:

```bash
# From repository root:
npm install -g wrangler
cd frontend
npm run build
cd ..
npx wrangler pages deploy frontend/dist --project-name=cse-4104-7a-t02
```
Or with Workers static assets:
```bash
npx wrangler deploy
```

---

## Step 5 — Alternative: Render Backend / Netlify Frontend

- **Render (Backend):** Blueprint in `render.yaml`. Build: `pip install -r requirements.txt`, Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- **Netlify (Frontend):** Blueprint in `netlify.toml`. Base: `frontend`, Build: `npm install && npm run build`, Publish: `dist`.

---

## Verification Checklist

1. Open Cloudflare URL (`https://your-app.pages.dev`).
2. Log in with demo credentials (`admin@example.com` / `admin123` or seeded account).
3. Confirm KPI cards load on the Dashboard.
4. Test AI Chatbot ("What was our best-selling product?").
5. Test PDF and CSV export.
6. Verify Status Indicator (System Diagnostics) shows green across Frontend, Backend (Vercel), and Database (Supabase).
