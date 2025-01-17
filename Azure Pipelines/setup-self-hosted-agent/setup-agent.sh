#!/bin/bash

# Required Parameters
ORG_NAME="$1"                   # Azure DevOps organization name
PAT="$2"                        # Personal Access Token
AGENT_POOL="$3"                 # Agent pool name

# Optional Parameters with Defaults
AGENT_VERSION="${4:-4.248.0}"   # Default agent version
AGENT_DIR="${5:-azure-pipelines-agent}"       # Default agent directory
AGENT_NAME="${6:-myAzureBuildAgent}"  # Default agent name
WORK_FOLDER="${7:-_work}"       # Default work folder

# Derived Variables
SERVER_URL="https://dev.azure.com/${ORG_NAME}"
AGENT_PACKAGE_URL="https://vstsagentpackage.azureedge.net/agent/${AGENT_VERSION}/vsts-agent-linux-x64-${AGENT_VERSION}.tar.gz"

# Install prerequisites
sudo apt update && sudo apt install -y wget tar

# Create agent directory
mkdir -p "$AGENT_DIR"
cd "$AGENT_DIR" || exit 1

# Download and extract the agent package
wget "$AGENT_PACKAGE_URL" -O agent.tar.gz
tar -zxvf agent.tar.gz

# Configure the agent
./config.sh --unattended \
    --url "$SERVER_URL" \
    --auth pat \
    --token "$PAT" \
    --pool "$AGENT_POOL" \
    --agent "$AGENT_NAME" \
    --work "$WORK_FOLDER" \
    --replace

# Install and start the agent as a service
sudo ./svc.sh install
sudo ./svc.sh start

# Cleanup
rm -f agent.tar.gz