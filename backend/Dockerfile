# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Minimal runtime deps for scientific Python wheels
# scikit-learn uses OpenMP -> libgomp1
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirement spec and install
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy source
COPY src /app/src

# Ensure Python can import the package from /app/src
ENV PYTHONPATH=/app/src

# Expose and run
ENV HOST=0.0.0.0 \
    PORT=5000
EXPOSE 5000

CMD ["python", "-m", "plagiarism_detector.api"]
