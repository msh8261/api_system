import os
import sys
import time

# Get the absolute path of the current file
current_file_path = os.path.abspath(__file__)
# Get the directory path of the current file
current_dir_path = os.path.dirname(current_file_path)
# Get the parent directory path
parent_dir_path = os.path.dirname(current_dir_path)
# Add the parent directory path to the sys.path
sys.path.insert(0, parent_dir_path)

from kafka import KafkaProducer
import json
from dotenv import load_dotenv
from backend.log import logger

# Load environment variables from .env file
load_dotenv()


bootstrap_servers=os.getenv("KAFKA_BROKER", 'localhost:9092, localhost:9093').split(',')

# Messages will be serialized as JSON 
def serializer(message):
    return json.dumps(message).encode()

def setup_producer():
    """
    create a KafkaProducer instance with bootstrap servers.
    Parameters:
    Returns:
    - KafkaProducer instance.
    """    
    try:
        producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=serializer
        )
        return producer
    except Exception as e:
        if e == 'NoBrokersAvailable':
            print('waiting for brokers to become available')
        return 'not-ready'


def send_message(topic, messages):
    """
    Send masseges to a topic by producer.
    Args:
    - Kafka_producer (object): used to send messages.
    - topic (string): a name of topic.
    - message (list): a list of messages.
    Returns: None
    """
    try:
        for message in messages:
            Kafka_producer = setup_producer()
            Kafka_producer.send(topic, value=message)
            # sleep time to prevent duplicated messages
            time.sleep(0.05)
        # Wait for all messages in the Producer queue to be delivered
        Kafka_producer.flush()
        logger.info(f"Massesge Sent to topic '{topic}'.")
    except Exception as e:
        logger.error(
            f"Failed to send messages \
                            topic '{topic}'."
        )