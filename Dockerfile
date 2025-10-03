# ---------------------------
# Stage 1: Builder
# ---------------------------
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc g++ libffi-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements for caching
COPY requirements.txt .

# Install Python packages into /install directory
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# ---------------------------
# Stage 2: Final minimal image
# ---------------------------
FROM python:3.11-slim

WORKDIR /app

# Install gunicorn only
RUN pip install --no-cache-dir gunicorn==21.2.0

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy app files
COPY . .

# Expose port for Cloud Run
EXPOSE 8080

# Set environment variable for Cloud Run (optional)
ENV PORT=8080

# Run gunicorn
CMD ["gunicorn", "--bind", ":8080", "--workers=2", "run:app"]
