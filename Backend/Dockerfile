FROM python:3.13-slim AS builder

WORKDIR /app

ENV UV_LINK_MODE=copy
ARG TF_FLAVOR=cpu

COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv \
	&& if [ "$TF_FLAVOR" != "cpu" ] && [ "$TF_FLAVOR" != "gpu" ]; then echo "Invalid TF_FLAVOR: $TF_FLAVOR" && exit 1; fi \
	&& uv sync --no-dev --python 3.13 --extra "$TF_FLAVOR"

COPY . .

RUN rm -rf /root/.cache/uv /root/.cache/pip


FROM python:3.13-slim AS runtime

WORKDIR /app

ENV PATH="/app/.venv/bin:${PATH}"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

COPY --from=builder /app /app

EXPOSE 8000

CMD ["sh", "-c", "gunicorn -w 1 -b 0.0.0.0:${PORT} --timeout 120 --access-logfile - --error-logfile - --log-level info main:app"]

