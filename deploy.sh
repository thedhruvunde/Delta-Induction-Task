#!/bin/bash
cd /app  # or wherever your project lives

echo "Pulling latest Docker image..."
docker-compose pull server

echo "Restarting services..."
docker-compose down
docker-compose up -d

echo "Deployment complete"
