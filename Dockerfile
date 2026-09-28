# Two-stage build producing ONE image that serves both the React client and
# the Flask API, so the deployed app is a single service on a single public
# URL (OPS-01 / R2-3).
#
# Stage 1 needs Node, stage 2 needs Python. Building this way is what lets a
# Python-only host run the app: Node exists only while the client is
# compiled and is absent from the shipped image.

# ---------------------------------------------------------------------------
# Stage 1: compile the React client to static files
# ---------------------------------------------------------------------------
FROM node:20-slim AS client-build

WORKDIR /client

# Copy manifests alone first so Docker can reuse the cached dependency layer
# whenever only application source changed.
COPY client/package.json client/package-lock.json ./
RUN npm ci

COPY client/ ./
RUN npm run build

# ---------------------------------------------------------------------------
# Stage 2: Python runtime serving the API and the compiled client
# ---------------------------------------------------------------------------
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY server/requirements.txt ./server/requirements.txt
RUN pip install --no-cache-dir -r server/requirements.txt

COPY server/ ./server/

# Bring over only the compiled output from stage 1 -- no node_modules, no
# Node runtime.
COPY --from=client-build /client/dist ./client/dist
ENV CLIENT_DIST=/app/client/dist

WORKDIR /app/server

# The host assigns the port at runtime via $PORT; 8000 is the local default.
# Shell form is required here so $PORT is expanded at start time.
EXPOSE 8000
CMD gunicorn --bind "0.0.0.0:${PORT:-8000}" --workers 2 --timeout 60 app:app
