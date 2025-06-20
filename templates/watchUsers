#!/bin/bash

YAML_FILE="/scripts/templates/users.yaml"
SCRIPT="/scripts/apps/initUsers"

while true; do
    inotifywait -e modify "$YAML_FILE"
    echo "$(date): Detected change in users.yaml, updating..." >> /var/log/users_sync.log
    bash "$SCRIPT" >> /var/log/users_sync.log 2>&1
done
