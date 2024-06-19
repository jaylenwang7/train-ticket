#!/bin/bash

# Set Docker Hub credentials as environment variables
source ./set-docker.sh

# Check if required environment variables are set
if [[ -z "$DOCKER_HUB_USERNAME" || -z "$DOCKER_HUB_PASSWORD" ]]; then
  echo "Error: DOCKER_HUB_USERNAME and DOCKER_HUB_PASSWORD environment variables must be set."
  exit 1
fi

# Log in to Docker Hub
echo "$DOCKER_HUB_PASSWORD" | docker login -u "$DOCKER_HUB_USERNAME" --password-stdin

# Loop through directories to build and push Docker images
for dir in $(find . -maxdepth 2 -type f -name Dockerfile -exec dirname {} \;); do
  echo "Building Docker image in directory: $dir"
  IMAGE_NAME=$(basename "$dir")
  
  # Tag the image with your Docker Hub username and repository
  docker build -t $DOCKER_HUB_USERNAME/$IMAGE_NAME:latest "$dir"
  
  # Push the image to Docker Hub
  docker push $DOCKER_HUB_USERNAME/$IMAGE_NAME:latest
done