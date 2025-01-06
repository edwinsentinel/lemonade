import os
import time
import requests
from prometheus_client import start_http_server, Gauge

# Environment variables
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
SCRAPE_INTERVAL = int(os.getenv("SCRAPE_INTERVAL", 15))

# Metrics
QUEUE_MESSAGES = Gauge(
    "rabbitmq_individual_queue_messages",
    "Total messages in RabbitMQ queue",
    ["host", "vhost", "name"],
)
QUEUE_MESSAGES_READY = Gauge(
    "rabbitmq_individual_queue_messages_ready",
    "Ready messages in RabbitMQ queue",
    ["host", "vhost", "name"],
)
QUEUE_MESSAGES_UNACK = Gauge(
    "rabbitmq_individual_queue_messages_unacknowledged",
    "Unacknowledged messages in RabbitMQ queue",
    ["host", "vhost", "name"],
)

def fetch_queue_metrics():
    """Fetch queue metrics from RabbitMQ HTTP API."""
    url = f"http://{RABBITMQ_HOST}:15672/api/queues"
    try:
        response = requests.get(url, auth=(RABBITMQ_USER, RABBITMQ_PASSWORD))
        response.raise_for_status()
        queues = response.json()

        for queue in queues:
            vhost = queue.get("vhost", "")
            name = queue.get("name", "")
            messages = queue.get("messages", 0)
            messages_ready = queue.get("messages_ready", 0)
            messages_unack = queue.get("messages_unacknowledged", 0)

            # Set Prometheus metrics
            QUEUE_MESSAGES.labels(host=RABBITMQ_HOST, vhost=vhost, name=name).set(messages)
            QUEUE_MESSAGES_READY.labels(host=RABBITMQ_HOST, vhost=vhost, name=name).set(messages_ready)
            QUEUE_MESSAGES_UNACK.labels(host=RABBITMQ_HOST, vhost=vhost, name=name).set(messages_unack)

    except requests.RequestException as e:
        print(f"Error fetching metrics: {e}")

def main():
    """Main function to start the exporter."""
    # Start Prometheus HTTP server
    start_http_server(8000)
    print("Prometheus RabbitMQ Exporter started on port 8000")

    # Periodically fetch metrics
    while True:
        fetch_queue_metrics()
        time.sleep(SCRAPE_INTERVAL)

if __name__ == "__main__":
    main()


#steps to use
#pip install prometheus_client requests
# set variable 
# #export RABBITMQ_HOST=<your-rabbitmq-host>
# export RABBITMQ_USER=<your-rabbitmq-user>
# export RABBITMQ_PASSWORD=<your-rabbitmq-password>
# run the script python rabbitmq_exporter.py

