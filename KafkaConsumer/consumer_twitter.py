from kafka import KafkaConsumer
import json

print("Setting up Kafka consumer for ProductHunt topic")
consumer = KafkaConsumer(
    'twitter-llm',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='producthunt-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')))

for message in consumer:
    data = message.value
    print(data)