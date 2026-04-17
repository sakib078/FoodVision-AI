# Render + Docker Deployment Guide

**Date:** April 13, 2026

## Goal
- Deploy FoodVision backend and frontend using Render with Docker.
- Keep deployment simple, free-tier friendly, and ready for MVP usage.

## Architecture
- Backend service on Render from [Backend/Dockerfile](Backend/Dockerfile)
- Frontend service on Render from [frontend/Dockerfile](frontend/Dockerfile)
- Frontend calls backend using environment variable `NEXT_PUBLIC_API_BASE_URL`

---

## Repo Files Used
- [render.yaml](render.yaml): Render Blueprint for both services
- [Backend/Dockerfile](Backend/Dockerfile): Gunicorn backend image
- [frontend/Dockerfile](frontend/Dockerfile): Next.js production image
- [frontend/app/page.tsx](frontend/app/page.tsx): API URL reads from env var

---

## Step 1: Push to GitHub
1. Commit your current code.
2. Push to GitHub.
3. Confirm these folders exist in repo root:
   - `Backend`
   - `frontend`

---

## Step 2: Create Services on Render
### Option A (Recommended): Blueprint
1. Open Render dashboard.
2. Click New > Blueprint.
3. Connect your GitHub repo.
4. Render reads [render.yaml](render.yaml) and creates two services:
   - `foodvision-backend`
   - `foodvision-frontend`

### Option B: Manual Setup
Create two Render Web Services from the same repo.

Backend service settings:
- Runtime: Docker
- Root Directory: `Backend`
- Dockerfile Path: `./Dockerfile`
- Plan: Free
- Health Check Path: `/health`

Frontend service settings:
- Runtime: Docker
- Root Directory: `frontend`
- Dockerfile Path: `./Dockerfile`
- Plan: Free

---

## Step 3: Set Environment Variables
Backend service:
- `PYTHONUNBUFFERED=1`

Frontend service:
- `NEXT_PUBLIC_API_BASE_URL=https://<your-backend-service>.onrender.com`

Important:
- Replace `<your-backend-service>` with your real backend Render service URL.
- Redeploy frontend after updating the env var.

---

## Step 4: Verify Backend
Open in browser:
- `https://<your-backend-service>.onrender.com/health`

Expected:
- HTTP 200 response
- Health payload from backend

---

## Step 5: Verify Frontend to Backend Flow
1. Open your frontend Render URL.
2. Upload an image.
3. Run prediction.
4. Confirm response appears in UI.

If it fails:
- Verify `NEXT_PUBLIC_API_BASE_URL` is correct.
- Check backend logs in Render dashboard.
- Check frontend logs in Render dashboard.

---

## Step 6: CORS Check
If browser shows CORS errors:
1. Add frontend Render domain to backend allowed origins.
2. Redeploy backend.
3. Retry from frontend.

---

## Step 7: Ongoing Deploy Workflow
1. Push changes to GitHub.
2. Render auto-deploys (if auto-deploy enabled).
3. For urgent fixes, trigger manual deploy in Render.

---

## Step 8: Rollback Plan
1. Open service in Render.
2. Go to Deploys.
3. Select last healthy deploy.
4. Click Rollback.

---

## Free Tier Notes
- Render free services can sleep after inactivity (cold starts).
- First request after sleep may be slow.
- This setup is CPU-only on free tier.
- GPU deployment requires a paid GPU platform.

---

## Quick Checklist
- [ ] Repo pushed to GitHub
- [ ] Backend service created on Render
- [ ] Frontend service created on Render
- [ ] `NEXT_PUBLIC_API_BASE_URL` set in frontend
- [ ] Backend `/health` returns 200
- [ ] Frontend prediction works end to end
