# Capstone
Tweet Analyzer

## Start Zookeeper, Kafka, Cassandra from docker image
```sh
# Zookeeper
docker run -d -p 2181:2181 -p 2888:2888 -p 3888:3888 --name zookeeper confluent/zookeeper

# Kafka
docker run -d -p 9092:9092 -e KAFKA_ADVERTISED_HOST_NAME=localhost -e KAFKA_ADVERTISED_PORT=9092 --name kafka --link zookeeper:zookeeper confluent/kafka

# Cassandra
docker run -d -p 7199:7199 -p 9042:9042 -p 9160:9160 -p 7001:7001 --name cassandra cassandra:3.7
```

## Start Producer, Storage
```sh
# Start data-producer
python data-producer.py tweet-analyzer 127.0.0.1:9092

# Start data-storage
python data-storage.py twttier-analyzer localhost:9092 tweet tweet localhost
```

## Use kafka consumer to read from kafka topic
open a python terminal
```python
from kafka import KafkaConsumer
consumer = KafkaConsumer('tweet-analyzer',bootstrap_servers='127.0.0.1:9092')
for msg in consumer:
	print(msg)