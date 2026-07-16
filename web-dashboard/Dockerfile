# web-dashboard/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies sistem untuk PostgreSQL
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements dan install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy seluruh source code
COPY . .

EXPOSE 5000

# Jalankan menggunakan Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]