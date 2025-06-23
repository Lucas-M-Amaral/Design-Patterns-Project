# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies (optional, required for some libs)
RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev

# Copy and install dependencies separately for caching
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Final stage (lightweight image)
FROM python:3.11-slim

WORKDIR /app

# Copy only what is needed from the previous stage
COPY --from=builder /root/.local /root/.local
COPY . .

# Ensures user scripts are found
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app

# Default variables (overridden by docker-compose)
ENV APP_HOST=0.0.0.0 APP_PORT=8000

# Exposes the port and runs the application
EXPOSE ${APP_PORT}
CMD ["uvicorn", "main:app", "--host", "${APP_HOST}", "--port", "${APP_PORT}", "--reload"]