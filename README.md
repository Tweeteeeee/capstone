# Capstone
Tweet Analyzer

## Requirements
```
# Install dependencies
pip install -r requirements.txt
```

## Pipeline
```
RawData -> Kafka -> Spark -> Kafka -> Redis -> Node.js
            |                 |  
             -> Cassandra      -> Cassandra      
```

## Start Zookeeper, Kafka, Cassandra, Redis from docker image
```sh
# Zookeeper
docker run -d -p 2181:2181 -p 2888:2888 -p 3888:3888 --name zookeeper confluent/zookeeper

# Kafka
docker run -d -p 9092:9092 -e KAFKA_ADVERTISED_HOST_NAME=localhost -e KAFKA_ADVERTISED_PORT=9092 --name kafka --link zookeeper:zookeeper confluent/kafka

# Cassandra
docker run -d -p 7199:7199 -p 9042:9042 -p 9160:9160 -p 7001:7001 --name cassandra cassandra:3.7

# Redis
docker run -d -p 6379:6379 --name redis redis:alpine
```

## Start Producer, Storage
```sh
# Start data-producer
python data-producer.py tweet-analyzer 127.0.0.1:9092

# Start data-storage
python data-storage.py tweet-analyzer localhost:9092 tweet tweet localhost

# Start Redis
python redis-publisher.py tweet-analyzer localhost:9092 tweet localhost 6379

# Start stream-processing.py
spark-submit --jars spark-streaming-kafka-0-8-assembly_2.11-2.0.0.jar stream-processing.py tweet-analyzer tweet-compute 127.0.0.1:9092
```

## Use kafka consumer to read from kafka topic
open a python terminal
```python
from kafka import KafkaConsumer
consumer = KafkaConsumer('tweet-analyzer',bootstrap_servers='127.0.0.1:9092')
for msg in consumer:
    print(msg)
```

## Read from cassandra
```sh
python data-processor.py tweet tweet localhost
```

## Read data from Redis channel
run redis-cli
```sh
/usr/local/Cellar/redis/4.0.2/bin/redis-cli -h localhost

SUBSCRIBE tweet
```

## Extract Twitter entities
According to Twitter doc, [tweet_object](https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/tweet-object)

```json
"entities":
{
    "hashtags":[],
    "urls":[],
    "user_mentions":[],
    "media":[],
    "symbols":[],
    "polls":[]
}
```

[Twitter-text-python](https://github.com/edburnett/twitter-text-python)

This package can be used to extract user_mentions, hashtags, URLs and format as HTML for display.

## Extract location
Extract place names from a URL or text

- [Geograpy](https://github.com/ushahidi/geograpy) - picked this one for now
- [geotext](https://github.com/elyase/geotext)

geograpy is more advanced and bigger in scope compared to geotext and can do everything geotext does. On the other hand geotext is leaner: has no external dependencies, is faster (re vs nltk) and also depends on libraries and data covered with more permissive licenses.
