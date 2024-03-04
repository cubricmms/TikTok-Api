# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

FROM mcr.microsoft.com/playwright/python:v1.32.0-jammy

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY poetry.lock pyproject.toml .

RUN pip install poetry && \
    poetry install

RUN playwright install --with-deps

# Copy the source code into the container.
COPY . .

# Run the application.
CMD  poetry run python scrape_tiktok.py
