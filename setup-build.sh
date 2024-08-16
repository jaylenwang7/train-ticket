#!/bin/bash

set -e

# Install maven
apt-get update
apt-get install -y maven

# Install java 8
apt-get install -y openjdk-8-jdk

# Check docker is installed
if ! [ -x "$(command -v docker)" ]; then
  echo 'Error: docker is not installed.' >&2
  exit 1
fi

# Switch java to version 8
update-alternatives --set java /usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java

# Clean up
mvn clean package -Dmaven.test.skip=true