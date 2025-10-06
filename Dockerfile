# Use Python slim image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies for mysqlclient and other build tools
RUN apt-get update && apt-get install -y \
    python3-dev \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first (caches better)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . .

# Expose port 8000
EXPOSE 8000

# Default command (can be overridden by docker-compose.yml)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
