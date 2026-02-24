#!/bin/bash
# Create Trading Nexus application in Coolify
# Run this on the VPS: bash create_app_coolify.sh

echo "Creating Trading Nexus application in Coolify..."
echo ""

curl -X POST \
  -H "Authorization: Bearer 2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Trading Nexus",
    "description": "Trading platform with Django backend and React frontend",
    "git_repository": "https://github.com/correspond9/Trading-nexus-v2.git",
    "git_branch": "main",
    "docker_compose_file": "docker-compose.yml",
    "type": "docker-compose",
    "port": "8000"
  }' \
  http://localhost:3000/api/v1/applications

echo ""
echo "Application creation request completed."
echo "Check Coolify dashboard for new application."
