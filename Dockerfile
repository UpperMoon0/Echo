# Echo Dockerfile - Speech-to-text service with Whisper
# Unified server supporting both HTTP REST API and JSON-RPC MCP over HTTP

# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install system dependencies for Whisper (ffmpeg)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# Copy the Echo directory content to the working directory
COPY . /app/Echo

# Set working directory to the application directory
WORKDIR /app/Echo

# Add current directory to Python path to enable relative imports
ENV PYTHONPATH=/app/Echo:$PYTHONPATH

# Expose the port the app runs on
EXPOSE 8000

# Single unified server - supports both HTTP REST API and Embedded MCP
CMD ["python", "main.py"]