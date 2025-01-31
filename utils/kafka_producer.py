from kafka import KafkaProducer
import os
import json

producer = KafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_BROKER", "localhost:9092"),
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def send_message(topic, message):
    producer.send(topic, message)
