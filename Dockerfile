# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1
# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/opt/venv/bin:$PATH" \
  VIRTUAL_ENV="/opt/venv"

WORKDIR /app

RUN apt-get update && \
  apt-get install -y --no-install-recommends \
    python3.10-venv=3.10.12-1~22.04.3 && \
    # x11vnc && \
  rm -rf /var/cache/apt/archives /var/lib/apt/lists/*

# RUN mkdir ~/.vnc && x11vnc -storepasswd 1234 ~/.vnc/passwd

COPY poetry.lock pyproject.toml /app/

RUN pip install --no-cache-dir poetry==1.8.2 && \
  python -m venv /opt/venv && \
  poetry install --no-interaction --no-dev && \
  rm -rf ~/.cache/pip ~/.cache/pypoetry/cache ~/.cache/pypoetry/artifacts

# RUN playwright install --with-deps chrome && \
#   rm -rf /var/cache/apt/archives /var/lib/apt/lists/*

# Copy the source code into the container.
COPY . .

# Run the application.
CMD xvfb-run python scrape_tiktok.py
