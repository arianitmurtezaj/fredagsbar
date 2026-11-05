FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.11.26 /uv /bin/uv

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    UV_PYTHON_DOWNLOADS=never

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev

COPY api.py app.py swagger.json ./

EXPOSE 5002 8501
CMD ["python", "api.py"]
