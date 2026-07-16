# scanner/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies sistem untuk library Face Recognition / OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    cmake \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements dan install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy seluruh source code
COPY . .

EXPOSE 5001

# Jalankan menggunakan Gunicorn
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5001", "app:app"]