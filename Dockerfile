FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Create new non-root uesr
RUN useradd -m -u 1000 beekeeper
WORKDIR /home/beekeeper/app


# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

# copy source files to the user files
COPY --chown=beekeeper:beekeeper . .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# expose port 8000
EXPOSE 8000

# switch to user for running
USER beekeeper

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/version')"

ENTRYPOINT ["uv", "run", "uvicorn"]
CMD ["main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]