FROM python:3.12-slim AS builder

# Copy uv binaries only into the builder stage
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Enable bytecode compilation and copy mode for cache mounts
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /home/beekeeper/app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


FROM python:3.12-slim AS runtime

RUN useradd -m -u 1000 beekeeper
WORKDIR /home/beekeeper/app

# Place the virtualenv at the front of PATH
ENV PATH="/home/beekeeper/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY --from=builder --chown=1000:1000 /home/beekeeper/app/.venv /home/beekeeper/app/.venv
COPY --from=builder --chown=1000:1000 /home/beekeeper/app/src /home/beekeeper/app/src

USER 1000:1000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/version')"]

ENTRYPOINT ["uvicorn"]
CMD ["main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]