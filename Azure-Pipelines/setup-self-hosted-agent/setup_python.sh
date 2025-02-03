#!/bin/bash

# Check if a Python version is provided as a parameter
if [ -z "$1" ]; then
    echo "Usage: $0 <python-version>"
    exit 1
fi

# Assign the provided Python version to a variable
PYTHON_VERSION=$1

# Install Python build tools
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update
sudo -E apt-get -y install python${PYTHON_VERSION} python${PYTHON_VERSION}-venv build-essential

# Install the specified Python version in a virtual environment in the agent's tool cache
full_version=$(eval "python${PYTHON_VERSION} -V" | cut -d ' ' -f 2)
mkdir -p Python/${full_version}
ln -s $(pwd)/Python/${full_version} $(pwd)/Python/${PYTHON_VERSION}
eval "python${PYTHON_VERSION} -m venv Python/${full_version}/x64"
touch Python/${full_version}/x64.complete

echo "Python ${PYTHON_VERSION} setup complete."