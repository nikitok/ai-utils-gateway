FROM python:3.12-slim

# upgrade dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    poppler-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
RUN uv sync --frozen --no-cache

# Run the application.
CMD ["/app/.venv/bin/fastapi", "run", "src/aiutils/main.py", "--port", "80", "--host", "0.0.0.0"]