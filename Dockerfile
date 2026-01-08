FROM python:3.14-slim

# Create non-root user
RUN groupadd -g 1000 dashuser && \
    useradd -u 1000 -g dashuser -m -s /bin/bash dashuser

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Create data directory
RUN mkdir /data && chown dashuser:dashuser /data
ENV DATA_DIR=/data

# Install dependencies
COPY requirements.txt .
RUN uv pip install --no-cache-dir --system -r requirements.txt

# Copy application source code
COPY --chown=dashuser:dashuser src .

# Switch to non-root user
USER dashuser

# Expose the port the app runs on
EXPOSE 8050

# Start the application
CMD ["gunicorn", "app:server", "--bind=0.0.0.0:8050"]
