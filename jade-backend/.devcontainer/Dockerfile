# First, build the application in the `/app` directory
FROM ghcr.io/astral-sh/uv:bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy 

# Configure the Python directory so it is consistent
ENV UV_PYTHON_INSTALL_DIR=/python

# Only use the managed Python version
ENV UV_PYTHON_PREFERENCE=only-managed

# Install Python before the project for caching
RUN uv python install 3.11

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \ 
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \ 
    uv sync --frozen --no-dev

# Then, use a final image without uv
FROM debian:bookworm-slim

# Install CA certificates to avoid SSL verification failures
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates
# Add app user
RUN useradd --create-home appuser

# Copy the Python version
COPY --from=builder --chown=python:python /python /python

# Copy the application from the builder
COPY --from=builder --chown=appuser:appuser /app /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

USER appuser
WORKDIR /app
# expose container port
EXPOSE 8000

# Run the application directly
ENTRYPOINT ["python", "-m", "src.ats.main"]