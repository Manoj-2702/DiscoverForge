from kafka import KafkaConsumer
import json


print("Setting up Kafka consumer")
consumer = KafkaConsumer(
    'Software',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')))

for message in consumer:
    data = message.value
    # Process the data
    print(data)
  
