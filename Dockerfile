FROM python:3.13.2-slim

# Set working directory to /app inside the container
WORKDIR /app

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.cargo/bin/uv /usr/local/bin/uv

# Copy all files from local root to /app in container
COPY . .

# Install dependencies with uv
RUN uv venv && \
    . .venv/bin/activate && \
    uv pip install -r requirements.txt

# Expose port
EXPOSE 5000

# Run the app (files are in /app)
CMD [".venv/bin/uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]