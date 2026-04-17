# Docker Improvement Guide (FoodVision Backend)

## Purpose
This guide documents the container improvements already implemented and provides a future roadmap for making the backend image smaller, faster, and production-ready.

## Current Improvements Implemented

### 1) Multi-stage Docker build (builder + runtime)
Implemented in [Dockerfile](Dockerfile).

What it does:
- Uses a `builder` stage to resolve/install dependencies.
- Uses a `runtime` stage to run only what is needed in production.
- Removes package manager caches before final stage copy.

Why it helps:
- Reduces image size by avoiding build-time leftovers in final image.
- Improves security by minimizing runtime surface.

When to use:
- Always for production images.
- Especially useful when dependencies are heavy (TensorFlow/CUDA).

---

### 2) Split image strategy (CPU vs GPU)
Implemented via `TF_FLAVOR` build arg and extras in [pyproject.toml](pyproject.toml).

Current flavors:
- `cpu`: installs `tensorflow`
- `gpu`: installs `tensorflow[and-cuda]`

Build commands:
```bash
cd Backend
docker build --build-arg TF_FLAVOR=cpu -t sakib067/foodvision-backend:3.0-cpu .
docker build --build-arg TF_FLAVOR=gpu -t sakib067/foodvision-backend:3.0-gpu .
```

Push commands:
```bash
docker push sakib067/foodvision-backend:3.0-cpu
docker push sakib067/foodvision-backend:3.0-gpu
```

Why it helps:
- CPU image stays much smaller for testing/staging.
- GPU image carries CUDA stack only when needed.

When to use:
- Use CPU image for local dev, CI smoke tests, and non-GPU infra.
- Use GPU image only on verified GPU runtime.

---

### 3) Startup and request logging via Gunicorn
Configured in [Dockerfile](Dockerfile) CMD with:
- `--access-logfile -`
- `--error-logfile -`
- `--log-level info`

Why it helps:
- Confirms whether traffic actually reaches the app.
- Makes debugging gateway vs app-level issues much faster.

When to use:
- Always in managed inference platforms.
- Critical when diagnosing 404/timeout/routing issues.

## How to choose image flavor

Use `-cpu` if:
- You do not need GPU acceleration.
- You want faster build/push/startup.
- You are validating endpoint routing and API behavior.

Use `-gpu` if:
- Platform truly provides GPU nodes and NVIDIA runtime.
- You need lower inference latency for real workloads.

## Known operational checks after deploy

1. Verify endpoint receives requests:
- Gunicorn access logs should show route hits.
- If requests are missing in app logs, issue is upstream (gateway/routing/auth).

2. Verify GPU attachment (for `-gpu` image):
- Check logs for CUDA/cuDNN availability.
- If logs show missing CUDA libs, runtime is falling back to CPU.

3. Verify route compatibility:
- Platform may call `/infer` while app expects `/predict`.
- Keep route aliases as needed for platform contracts.

## Recommended next improvements

### A) Run as non-root user
Add a non-root user in runtime stage and switch with `USER`.

Why:
- Better container security posture.

### B) Add explicit healthcheck
Use Docker `HEALTHCHECK` with `/health` endpoint.

Why:
- Faster failure detection and better orchestration behavior.

### C) Pin base image by digest
Pin `python:3.13-slim` to a known digest.

Why:
- Reproducible builds and safer rollbacks.

### D) Separate model artifact from image (optional)
Store model in object storage and mount/download at startup.

Why:
- Smaller image and faster pushes.
- Easier model version rollout without full app rebuild.

### E) Add build cache optimization in CI
Use buildx cache (`--cache-from`, `--cache-to`) in CI pipeline.

Why:
- Faster repeated builds.

### F) Add security scanning gate
Scan image in CI (for example Trivy/Grype) before push.

Why:
- Early vulnerability detection.

### G) Tune Gunicorn worker model per workload
Current setting is `-w 1` (good for heavy ML memory usage).

Possible future tuning:
- Keep `-w 1` for large TF model memory safety.
- Increase workers only after profiling memory and latency.

## Troubleshooting quick map

- Symptom: endpoint is Ready but no app logs.
  - Likely issue: gateway/routing/auth upstream.

- Symptom: `POST /infer` returns 404 in app logs.
  - Likely issue: route mismatch between platform and app.

- Symptom: GPU usage is 0 and CUDA errors in logs.
  - Likely issue: platform GPU runtime/driver injection missing.

- Symptom: image too large.
  - Use `-cpu` flavor for non-GPU paths and keep multi-stage runtime.

## Change log summary (this project)
- Added multi-stage Docker build.
- Added CPU/GPU split via `TF_FLAVOR` and optional dependencies.
- Enabled Gunicorn access/error logs for deploy diagnostics.
- Kept runtime command stable for platform deployment.
