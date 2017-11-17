# Capstone
Tweet Analyzer

## Requirements
```
# Install dependencies
pip install -r requirements.txt
```

## Pipeline
```
RawData -> Kafka -> Spark -> Kafka -> Redis ---> ELK
            ╰> Cassandra -> Pig -> Cassandra -╯
```

## Start Zookeeper, Kafka, Cassandra, Redis from docker image
```sh
# Zookeeper
docker run -d -p 2181:2181 -p 2888:2888 -p 3888:3888 --name zookeeper confluent/zookeeper

# Kafka
docker run -d -p 9092:9092 -e KAFKA_ADVERTISED_HOST_NAME=localhost -e KAFKA_ADVERTISED_PORT=9092 --name kafka --link zookeeper:zookeeper confluent/kafka

# Cassandra cluster[1]
docker run -d -p 7199:7199 -p 9042:9042 -p 9160:9160 -p 7001:7001 --name cass1 cassandra:2.1.19

# In case this is the first time starting up cassandra we need to ensure
        # that all nodes do not start up at the same time. Cassandra has a
        # 2 minute rule i.e. 2 minutes between each node boot up.This only needs to happen the firt
        # time we bootup. Configuration below assumes if the Cassandra data
        # directory is empty it means that we are starting up for the first
        # time.

#check IP address : docker exec cass1 cat /etc/hosts

docker run -d  --name cass2 -e CASSANDRA_SEEDS="xxx.xxx.xxx.xxx" cassandra:2.1.19

docker run -d  --name cass3 -e CASSANDRA_SEEDS="xxx.xxx.xxx.xxx" cassandra:2.1.19

# verify cluster
docker exec cass1 nodetool status

# commented out previous way to run cassandra
# docker run -d -p 7199:7199 -p 9042:9042 -p 9160:9160 -p 7001:7001 --name cassandra cassandra:3.7

# Redis
docker run -d -p 6379:6379 --name redis redis:alpine
```

[1] For pig to be able to read from Cassandra, has to use cassandra:2.1.x

See [class CqlStorage is not there in latest versions of apache-cassandra-X.X.X.jar](https://stackoverflow.com/questions/34300458/why-the-class-cqlstorage-is-not-there-in-latest-versions-of-apache-cassandra-x-x/34300572)

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

## Read data from cassandra
```sh
python data-processor.py tweet tweet localhost
```

## Read data from redis channel
run redis-cli
```sh
/usr/local/Cellar/redis/4.0.2/bin/redis-cli -h localhost

SUBSCRIBE tweet
```
## pig load data from cassandra
```sh
# start pig docker image
docker run -d -P -p 2222:22 -p 8000:8000 -p 19888:19888 -p 8088:8088 -p 50070:50070 -v /path_to_capstone/capstone:/src --name pig daijyc/week2_1

cd hadoop-2.7.3/
./start-all.sh
export PIG_INITIAL_ADDRESS=192.168.1.100; # replace with your ip address
# find your host machine ip address, go to a new terminal
ifconfig | grep inet
export PIG_RPC_PORT=9160;
export PIG_PARTITIONER=org.apache.cassandra.dht.Murmur3Partitioner;

pig tweet-count-cassandra.pig
# check job running status in http://localhost:8088/
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
