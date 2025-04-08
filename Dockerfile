FROM python:3.13.2-slim

WORKDIR /app

# Install curl
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install uv and move it from /root/.local/bin/ to /usr/local/bin/
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.local/bin/uv /usr/local/bin/uv && \
    uv --version

# Copy project files
COPY pyproject.toml .
COPY . .

# Install dependencies with uv
RUN uv sync

# Expose port
EXPOSE 5000

# Run with uvicorn from the virtual environment
CMD [".venv/bin/uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]