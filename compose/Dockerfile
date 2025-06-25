# Multi-stage build for optimized production image
FROM python:3.11.9-slim-bullseye AS python-build-stage

# System dependencies for build stage
RUN apt-get update && apt-get install -y \
    binutils \
    libproj-dev \
    gdal-bin \
    build-essential \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip wheel --wheel-dir /usr/src/app/wheels -r requirements.txt

# Runtime stage
FROM python:3.11.9-slim-bullseye AS python-run-stage

ARG APP_HOME=/app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR ${APP_HOME}

# Runtime system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gettext \
    libgdal-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from build stage
COPY --from=python-build-stage /usr/src/app/wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
    && rm -rf /wheels

# Copy application files
COPY . ${APP_HOME}

COPY ./compose/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint && chmod +x /entrypoint

COPY ./compose/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

ENTRYPOINT ["/entrypoint"]