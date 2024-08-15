#!/bin/bash

set -euxo pipefail

# Function to prompt for credentials and write to file
prompt_and_write_credentials() {
    local env_file="./set-docker.sh"
    
    read -p "Enter Docker Hub username: " username
    read -sp "Enter Docker Hub password: " password
    echo

    echo "export DOCKER_HUB_USERNAME='$username'" > "$env_file"
    echo "export DOCKER_HUB_PASSWORD='$password'" >> "$env_file"
    
    echo "Credentials written to $env_file"
}

# Parse command line arguments
suffix=""
while getopts ":s:" opt; do
    case $opt in
        s) suffix="$OPTARG" ;;
        \?) echo "Invalid option -$OPTARG" >&2; exit 1 ;;
    esac
done

# Source Docker Hub credentials from environment file
if [ -f ./set-docker.sh ]; then
    source ./set-docker.sh
fi

# Check if required environment variables are set, prompt if not
if [[ -z "$DOCKER_HUB_USERNAME" || -z "$DOCKER_HUB_PASSWORD" ]]; then
    echo "Docker Hub credentials not found in environment."
    prompt_and_write_credentials
    source ./set-docker.sh
fi

# Log in to Docker Hub
echo "$DOCKER_HUB_PASSWORD" | docker login -u "$DOCKER_HUB_USERNAME" --password-stdin

# Loop through directories to build and push Docker images
for dir in $(find . -maxdepth 2 -type f -name Dockerfile -exec dirname {} \;); do
    echo "Building Docker image in directory: $dir"
    IMAGE_NAME=$(basename "$dir")
    
    # Add suffix to image name if provided
    if [ -n "$suffix" ]; then
        IMAGE_NAME="${IMAGE_NAME}-${suffix}"
    fi
    
    # Tag the image with your Docker Hub username and repository
    docker build -t $DOCKER_HUB_USERNAME/$IMAGE_NAME:latest "$dir"
    
    # Push the image to Docker Hub
    docker push $DOCKER_HUB_USERNAME/$IMAGE_NAME:latest
done