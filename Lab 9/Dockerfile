# Use a stable Python 3.11 base image
FROM python:3.11-slim-bookworm

# Install system dependencies needed to build llama-cpp-python
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install the Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# This container will be managed by docker-compose,
# which will mount the local code into /app