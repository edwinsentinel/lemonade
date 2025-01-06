#!/bin/bash

# Threshold for CPU usage
CPU_THRESHOLD=80
# Service name for Laravel backend
SERVICE_NAME="laravel-backend"

# Function to get the current CPU usage
get_cpu_usage() {
    # Get average CPU usage from top command
    # The `awk` filters the line with CPU usage
    top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}' | cut -d'.' -f1
}

# Function to restart the Laravel service
restart_service() {
    echo "CPU usage exceeded $CPU_THRESHOLD%. Restarting $SERVICE_NAME service..."
    sudo systemctl restart "$SERVICE_NAME"
    if [[ $? -eq 0 ]]; then
        echo "$SERVICE_NAME service restarted successfully."
    else
        echo "Failed to restart $SERVICE_NAME service."
    fi
}

# Monitor CPU usage
while true; do
    CPU_USAGE=$(get_cpu_usage)

    if (( CPU_USAGE > CPU_THRESHOLD )); then
        restart_service
    fi

    # Sleep for 5 seconds before re-checking
    sleep 5
done
