# SalesIQ — Production Deployment Guide

**CSE4104-7A-T02 | Northern University of Business and Technology, Khulna**

---

## Architecture

```
Browser
  │
  ▼
Vercel (React Frontend)
  │ HTTPS REST
  ▼
Render (FastAPI Backend)
  ├──► Supabase (PostgreSQL)
  └──► Gemini API (AI)
```

**Alternative:** Netlify instead of Vercel · Railway instead of Render

---

## Environment Variable Matrix

| Variable | Backend (Render) | Frontend (Vercel) | Type |
|---|---|---|---|
| `DATABASE_URL` | ✅ Required | ❌ Never | SECRET |
| `JWT_SECRET` | ✅ Required | ❌ Never | SECRET |
| `AI_PROVIDER` | ✅ Required | ❌ Never | config |
| `GEMINI_API_KEY` | ✅ Required | ❌ Never | SECRET |
| `GEMINI_MODEL` | ✅ Required | ❌ Never | config |
| `CORS_ORIGINS` | ✅ Required | ❌ Never | config |
| `ENVIRONMENT` | ✅ `production` | ❌ Never | config |
| `LOG_LEVEL` | ✅ `INFO` | ❌ Never | config |
| `VITE_API_BASE_URL` | ❌ Never | ✅ Required | PUBLIC |

> `VITE_*` variables are bundled into the browser JavaScript. **Never put secrets in them.**

---

## Prerequisites

- GitHub account with this repository pushed
- Google account (for Gemini API key)
- Supabase account (free tier: supabase.com)
- Render account (free tier: render.com)
- Vercel account (free tier: vercel.com)

---

## Step 1 — Supabase Database

### MANUAL ACTION REQUIRED

1. Go to **supabase.com** → New Project
2. Choose a name (e.g. `salesiq`), set a strong database password, choose nearest region
3. Wait for project to provision (~2 minutes)
4. Go to **Project Settings → Database**
5. Copy the **Connection String** (URI format):
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-REF].supabase.co:5432/postgres
   ```
6. Append `?sslmode=require` to the end:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-REF].supabase.co:5432/postgres?sslmode=require
   ```
   Save this — it becomes `DATABASE_URL` on Render.

### Run Migrations Against Supabase

After backend is deployed (Step 2), Render will run `alembic upgrade head` automatically via the build step — **or** you can run it manually from your local machine:

```bash
cd backend
DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres?sslmode=require" \
  alembic upgrade head
```

### Seed Initial Data (Optional)

To seed users, products, regions, and sample sales:

```bash
cd backend
DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres?sslmode=require" \
  python seed.py
```

> ⚠️ Seed creates demo users with known passwords (`admin123`, `manager123`, `viewer123`).
> Change these passwords immediately after seeding in production.

---

## Step 2 — Render Backend

### MANUAL ACTION REQUIRED

1. Go to **render.com** → New → **Web Service**
2. Connect your GitHub account and select repository `CSE-4104-7A-T02`
3. Configure:
   - **Name:** `salesiq-backend`
   - **Root Directory:** `backend`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt && alembic upgrade head`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Python Version:** `3.11`

4. Under **Environment Variables**, add:

   | Key | Value |
   |---|---|
   | `DATABASE_URL` | *(paste Supabase connection string with `?sslmode=require`)* |
   | `JWT_SECRET` | *(generate a random 64-char string — see below)* |
   | `AI_PROVIDER` | `gemini` |
   | `GEMINI_API_KEY` | *(your Google AI Studio key)* |
   | `GEMINI_MODEL` | `gemini-flash-latest` |
   | `CORS_ORIGINS` | *(leave blank for now, update after frontend deploy)* |
   | `ENVIRONMENT` | `production` |
   | `LOG_LEVEL` | `INFO` |

5. Click **Create Web Service**

### Generate JWT_SECRET

Run this locally to generate a strong secret:
```bash
python -c "import secrets; print(secrets.token_hex(64))"
```

### After Deployment

Note the Render URL: `https://salesiq-backend.onrender.com`

Verify:
```
https://salesiq-backend.onrender.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "healthy",
  "ai_provider": "gemini",
  "ai_configured": true
}
```

> ⚠️ Render free tier **sleeps after 15 minutes of inactivity**. The first request after sleep takes ~30 seconds. Upgrade to a paid plan to eliminate this.

---

## Step 3 — Update CORS After Backend is Live

### MANUAL ACTION REQUIRED

Once you know the Render backend URL, update `CORS_ORIGINS` in Render environment variables:

```
CORS_ORIGINS=https://your-app.vercel.app
```

(Do this after you know the Vercel URL from Step 4.)

---

## Step 4 — Vercel Frontend

### MANUAL ACTION REQUIRED

1. Go to **vercel.com** → New Project → Import from GitHub
2. Select repository `CSE-4104-7A-T02`
3. Configure:
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`

4. Under **Environment Variables**, add:

   | Key | Value |
   |---|---|
   | `VITE_API_BASE_URL` | `https://salesiq-backend.onrender.com` |

   > Use your actual Render URL. Do NOT add trailing slash.

5. Click **Deploy**

6. Note the Vercel URL: `https://your-app.vercel.app`

7. Go back to **Render → Environment Variables** and update:
   ```
   CORS_ORIGINS=https://your-app.vercel.app
   ```
   Then click **Manual Deploy → Deploy latest commit** on Render.

---

## Step 5 — Verify Full Application

Open the Vercel URL in Chrome and test:

```
Login with admin credentials
  ↓
Dashboard loads KPIs
  ↓
Sales Records page
  ↓
AI Insights → Generate
  ↓
Chatbot: "Hello"
  ↓
Chatbot: "What was our best-selling product?"
  ↓
Forecast page
  ↓
Reports → Export CSV
  ↓
Reports → Export PDF
  ↓
Notifications page
  ↓
Settings page
```

If any step fails, check Chrome DevTools → Network for the failing request and its response.

---

## Alternative: Netlify (instead of Vercel)

1. **netlify.com** → New Site → Import from Git
2. Select repository, branch: `main`
3. Build settings are read from `netlify.toml` automatically:
   - Base: `frontend`
   - Build: `npm install && npm run build`
   - Publish: `dist`
4. Add environment variable: `VITE_API_BASE_URL=https://your-backend.onrender.com`
5. Deploy

The `netlify.toml` already includes SPA redirect rules so direct URLs like `/dashboard` work correctly.

---

## Alternative: Railway (instead of Render)

1. **railway.app** → New Project → Deploy from GitHub
2. Select repository
3. Add service → select the repo
4. Set environment variables (same as Render above)
5. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Set root directory: `backend`

Railway auto-detects Python and installs requirements. It does not sleep on the free tier (but has a monthly usage limit).

---

## Rollback

**Frontend (Vercel):** Vercel → Project → Deployments → click any previous deployment → "..." → Promote to Production

**Backend (Render):** Render → Service → Deploys → click previous deploy → Rollback

**Database:** Supabase does not auto-rollback. Before any destructive migration:
```bash
alembic downgrade -1
```

---

## Security Checklist

- [ ] `backend/.env` is in `.gitignore` and NOT committed to GitHub
- [ ] `JWT_SECRET` is a randomly generated 64-char hex string, not the default
- [ ] `GEMINI_API_KEY` is only in Render environment variables
- [ ] `DATABASE_URL` is only in Render environment variables
- [ ] `CORS_ORIGINS` is set to exact Vercel/Netlify URL (no wildcard)
- [ ] `ENVIRONMENT=production` is set on Render (disables Swagger UI)
- [ ] Frontend build output (`frontend/dist`) contains no secrets
- [ ] Supabase database password is strong and unique
- [ ] Demo user passwords changed after seeding

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| Frontend API calls fail | `VITE_API_BASE_URL` wrong or not set | Set to Render HTTPS URL in Vercel env vars, redeploy frontend |
| CORS error in browser | `CORS_ORIGINS` doesn't match frontend URL | Update on Render, redeploy backend |
| `502 Bad Gateway` on Render | Backend crashed on startup | Check Render logs — likely DB connection failure |
| DB connection error | `DATABASE_URL` missing `?sslmode=require` | Append it to connection string on Render |
| Chatbot gives generic answers | `GEMINI_API_KEY` not set or wrong | Check `AI_PROVIDER=gemini` and key on Render |
| Render service sleeps | Free tier limitation | Upgrade to Render Starter plan ($7/month) |
| Alembic migration fails | Table already exists (from manual `create_all`) | Run `alembic stamp head` then `alembic upgrade head` |
| `/dashboard` returns 404 on Netlify | SPA redirect missing | `netlify.toml` already handles this |

---

## Free Tier Limits Reference

| Service | Free Tier Limit |
|---|---|
| Render | 750 hrs/month, sleeps after 15 min idle |
| Supabase | 500MB DB, 2GB bandwidth, 50,000 MAU |
| Vercel | 100GB bandwidth, unlimited deployments |
| Netlify | 100GB bandwidth, 300 build minutes |
| Gemini API | 1,500 requests/day (Flash model) |
