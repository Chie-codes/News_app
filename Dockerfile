# Use official Python image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the project files
COPY . .

# Expose port 8000
EXPOSE 8000

# Run migrations and start the server
CMD python manage.py migrate && python manage.py runserver 0.0.0.0:8000
