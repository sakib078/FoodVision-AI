# FoodVision Production Guide (Vercel + Render Docker Backend)

Date: April 17, 2026

## Goal
- Frontend on Vercel from your existing GitHub repository.
- Backend on Render using Docker runtime.
- Keep free-tier behavior predictable with keep-alive strategy.

## Final Architecture
- Frontend: Vercel (Next.js, root directory: `frontend`).
- Backend: Render Web Service (Docker, root directory: `Backend`).
- Frontend calls backend using `NEXT_PUBLIC_API_BASE_URL`.

---

## 1. Keep/Remove Files for This Setup

Keep:
- `Backend/Dockerfile` (required for Render Docker runtime backend)
- `render.yaml` (optional but recommended for reproducible Render setup)

Not required:
- `frontend/Dockerfile` (not used when frontend is deployed to Vercel normally)

---

## 2. Render Backend (Docker Runtime)

### Option A: Deploy with render.yaml (recommended)

Your `render.yaml` now contains only backend Docker service, which is correct for this architecture.

Steps:
1. Push latest code to GitHub.
2. In Render, create a Blueprint deployment from repo.
3. Confirm service settings:
   - Type: Web Service
   - Runtime: Docker
   - Root directory: `Backend`
   - Dockerfile path: `./Dockerfile`
   - Health check path: `/health`
4. Deploy.

### Option B: Deploy manually in Render UI

1. New Web Service -> connect repo.
2. Runtime: Docker.
3. Root Directory: `Backend`.
4. Dockerfile Path: `./Dockerfile`.
5. Plan: Free (or paid to avoid sleep).
6. Deploy.

Verify backend:

```bash
curl https://YOUR_RENDER_BACKEND_URL/health
```

---

## 3. Vercel Frontend (GitHub Repo)

1. Import the same repository in Vercel.
2. Set Root Directory to `frontend`.
3. Framework preset: Next.js.
4. Add environment variables in Vercel project:

- `NEXT_PUBLIC_API_BASE_URL=https://YOUR_RENDER_BACKEND_URL`
- `NEXT_PUBLIC_KEEP_ALIVE_ENABLED=true`
- `NEXT_PUBLIC_KEEP_ALIVE_INTERVAL_MS=840000`

5. Deploy.

---

## 4. Free Tier Sleep: What Actually Works

You already asked for frontend-triggered keep-alive. This repo now includes that behavior.

Current behavior:
- Browser pings backend `/health` every configured interval.
- Ping runs in production when the page is open and visible.

Important limitation:
- If no one has your site open, browser-based keep-alive cannot run.

Recommended stronger keep-awake path:
- Use an external monitor (UptimeRobot, Better Stack, cron-job.org)
- Ping:

```text
https://YOUR_RENDER_BACKEND_URL/health
```

- Suggested interval: every 10-14 minutes.

---

## 5. CORS + API Validation

If frontend loads but prediction fails:

1. Confirm Vercel env var points to Render backend URL.
2. Confirm backend CORS allows your Vercel domain.
3. Test backend directly:

```bash
curl https://YOUR_RENDER_BACKEND_URL/health
curl -X POST https://YOUR_RENDER_BACKEND_URL/predict
```

---

## 6. Update Workflow

Backend updates:
1. Push to GitHub.
2. Render auto-deploys backend.
3. Verify `/health` and one `/predict` request.

Frontend updates:
1. Push to GitHub.
2. Vercel auto-deploys frontend.
3. Verify API requests in browser network tab.

If backend URL changes, update `NEXT_PUBLIC_API_BASE_URL` in Vercel and redeploy.

---

## 7. Fly.io 7-Day Trial (Fallback)

Use Fly.io as a short validation environment only:
- Keep frontend on Vercel.
- Deploy backend on Fly.io for performance comparison.

Because trial is short, do not treat it as stable production unless you plan paid continuation.

---

## 8. Quick Checklist

- Backend deployed on Render Docker runtime.
- Backend `/health` returns healthy.
- Frontend deployed on Vercel from GitHub.
- `NEXT_PUBLIC_API_BASE_URL` points to backend.
- Keep-alive env vars set in Vercel.
- CORS allows Vercel frontend origin.
- Webcam + upload prediction flows tested on desktop and mobile.
