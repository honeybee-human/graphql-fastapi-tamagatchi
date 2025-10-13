# Multi-stage Dockerfile: build Vue frontend, run FastAPI backend

# --- Frontend build stage ---
FROM node:18-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
ENV NODE_ENV=development
RUN npm ci
COPY frontend/ ./
RUN npm run build

# --- Backend runtime stage ---
FROM python:3.11-slim AS backend
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

# Install Python deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source and data
COPY app/ ./app/
COPY game_data.json ./

# Copy built frontend assets from previous stage
COPY --from=frontend-build /frontend/dist ./frontend/dist

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]