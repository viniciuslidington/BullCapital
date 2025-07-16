# market_data_downloader_service/Dockerfile
# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy only the packaging configuration first to leverage Docker's layer caching.
# This layer will only be rebuilt if pyproject.toml changes.
COPY pyproject.toml .

# Install the project and its dependencies defined in pyproject.toml
# The '.' tells pip to install the project in the current directory
RUN pip install --no-cache-dir .

# Copy the rest of the application source code
COPY . .

# The command to run the service is specified in docker-compose.yml
CMD ["python", "main.py"]