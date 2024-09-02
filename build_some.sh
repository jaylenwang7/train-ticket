#!/bin/bash

# Set Docker Hub credentials as environment variables
source ./set-docker.sh

# Check if required environment variables are set
if [[ -z "$DOCKER_HUB_USERNAME" || -z "$DOCKER_HUB_PASSWORD" ]]; then
  echo "Error: DOCKER_HUB_USERNAME and DOCKER_HUB_PASSWORD environment variables must be set."
  exit 1
fi

# Check if the file containing the list of directories is provided
if [[ $# -eq 0 ]]; then
  echo "Usage: $0 <path_to_directory_list_file>"
  exit 1
fi

DIRECTORY_LIST_FILE="$1"

# Check if the file exists
if [[ ! -f "$DIRECTORY_LIST_FILE" ]]; then
  echo "Error: File '$DIRECTORY_LIST_FILE' not found."
  exit 1
fi

# Log in to Docker Hub
echo "$DOCKER_HUB_PASSWORD" | docker login -u "$DOCKER_HUB_USERNAME" --password-stdin

# Loop through directories listed in the file to build and push Docker images
while IFS= read -r dir || [[ -n "$dir" ]]; do
  # Remove leading/trailing whitespace
  dir=$(echo "$dir" | xargs)
  
  if [[ -z "$dir" ]]; then
    continue  # Skip empty lines
  fi
  
  if [[ ! -d "$dir" ]]; then
    echo "Warning: Directory '$dir' not found. Skipping."
    continue
  fi
  
  if [[ ! -f "$dir/Dockerfile" ]]; then
    echo "Warning: No Dockerfile found in '$dir'. Skipping."
    continue
  }
  
  echo "Building Docker image in directory: $dir"
  IMAGE_NAME=$(basename "$dir")
  
  # Tag the image with your Docker Hub username and repository
  docker build -t $DOCKER_HUB_USERNAME/$IMAGE_NAME:latest "$dir"
  
  # Push the image to Docker Hub
  docker push $DOCKER_HUB_USERNAME/$IMAGE_NAME:latest
done < "$DIRECTORY_LIST_FILE"