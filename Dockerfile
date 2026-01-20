# Echo Dockerfile - Speech-to-text service with Whisper
# Unified server supporting both HTTP REST API and JSON-RPC MCP over HTTP

# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install system dependencies for Whisper (ffmpeg)
# Use cache mount to speed up apt-get and persist cache between builds
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    rm -f /etc/apt/apt.conf.d/docker-clean && \
    apt-get update && apt-get install -y \
    ffmpeg

# Set the working directory in the container
WORKDIR /app

# Install heavy dependencies first to leverage Docker layer caching
# We do this BEFORE copying requirements.txt so changes to requirements don't trigger a torch reinstall
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install torch torchaudio openai-whisper

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Filter out torch, torchaudio, and openai-whisper as they are already installed
RUN --mount=type=cache,target=/root/.cache/pip \
    grep -vE "^torch|^torchaudio|^openai-whisper" requirements.txt > requirements-filtered.txt && \
    pip install -r requirements-filtered.txt

# Copy the Echo directory content to the working directory
COPY . /app/Echo

# Set working directory to the application directory
WORKDIR /app/Echo

# Add current directory to Python path to enable relative imports
ENV PYTHONPATH=/app/Echo

# Expose the port the app runs on
EXPOSE 8000

# Single unified server - supports both HTTP REST API and Embedded MCP
CMD ["python", "main.py"]