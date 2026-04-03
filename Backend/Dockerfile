FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
RUN pip install --no-cache-dir uv && uv sync --frozen --no-dev --python 3.13

COPY . .

EXPOSE 8000

CMD ["uv", "run", "main.py"]

