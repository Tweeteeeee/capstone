# Capstone
Tweet Analyzer

## Document
[Proposal](https://docs.google.com/document/d/1fgB14sUzIrOSmZvBAXYs-taQJIpIAaeLCIw9hA8ErQI/edit#heading=h.h8arf2uqoqk1)

[PPT](https://docs.google.com/presentation/d/1sY_qxrlaWQfmARrHLL_aLZ48u5H9R8zkpd3MfmSdX98/edit#slide=id.p3)

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

# Cassandra [1]
docker run -d -p 7199:7199 -p 9042:9042 -p 9160:9160 -p 7001:7001 --name cassandra cassandra:2.1.19

# commented out previous way to run cassandra
# docker run -d -p 7199:7199 -p 9042:9042 -p 9160:9160 -p 7001:7001 --name cassandra cassandra:3.7

# Redis
docker run -d -p 6379:6379 --name redis redis:alpine
```

[1] For pig to be able to read from Cassandra, has to use cassandra:2.1.x

See [class CqlStorage is not there in latest versions of apache-cassandra-X.X.X.jar](https://stackoverflow.com/questions/34300458/why-the-class-cqlstorage-is-not-there-in-latest-versions-of-apache-cassandra-x-x/34300572)

## Cluster Mode
```sh
# Kafka cluster
Scale up the kafka nodes. In this example it will increase kafka nodes to 4.

./kafka-cluster.sh scale 4

# Cassandra cluster
docker run -d -p 7199:7199 -p 9042:9042 -p 9160:9160 -p 7001:7001 --name cass1 cassandra:2.1.19

# In case this is the first time starting up cassandra we need to ensure
        # that all nodes do not start up at the same time. Cassandra has a
        # 2 minute rule i.e. 2 minutes between each node boot up.This only needs to happen the first
        # time we bootup. Configuration below assumes if the Cassandra data
        # directory is empty it means that we are starting up for the first
        # time.

# check IP address
docker exec cass1 cat /etc/hosts

docker run -d  --name cass2 -e CASSANDRA_SEEDS="xxx.xxx.xxx.xxx" cassandra:2.1.19

docker run -d  --name cass3 -e CASSANDRA_SEEDS="xxx.xxx.xxx.xxx" cassandra:2.1.19

# verify cluster
docker exec cass1 nodetool status
```

## Start Data Producer, Storage
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

## Verification Steps

### Use kafka consumer to read from kafka topic
open a python terminal
```python
from kafka import KafkaConsumer
consumer = KafkaConsumer('tweet-analyzer',bootstrap_servers='127.0.0.1:9092')
for msg in consumer:
    print(msg)
```

### Read data from cassandra
```sh
python data-processor.py tweet tweet localhost
```

### Read data from redis channel
```sh
# run redis-cli
/usr/local/Cellar/redis/4.0.2/bin/redis-cli -h localhost
SUBSCRIBE tweet
```

## pig load/store data from/to cassandra
```sh
# start pig docker container
docker run -d -P -p 2222:22 -p 8000:8000 -p 19888:19888 -p 8088:8088 -p 50070:50070 -v /path_to_capstone/capstone:/src --name pig daijyc/week2_1

cd hadoop-2.7.3/
./start-all.sh
export PIG_RPC_PORT=9160;
export PIG_PARTITIONER=org.apache.cassandra.dht.Murmur3Partitioner;
export PIG_INITIAL_ADDRESS=192.168.1.100; # replace with your ip address
# this ip address can be the ip address of your host machine or cassandra docker container
# find your host machine ip address, go to a new terminal, outside of pig docker container
ifconfig | grep inet
# or find ip address of the running cassandra docker container
docker exec cassandra cat /etc/hosts

# create tables in cassandra, go to a new terminal, outside of pig docker container
docker exec -it cassandra bash
./usr/bin/cqlsh
CREATE TABLE tweetcount (tweet_location text, tweet_count bigint, PRIMARY KEY (tweet_location));
CREATE TABLE hashtagcount (hashtag text, count bigint, PRIMARY KEY (hashtag));
# check if tweetcount, hashtagcount tables are created
DESCRIBE KEYSPACE tweet

# go back to pig docker container
cd /src/pig-scripts
pig tweet-count-cassandra.pig
pig hahstags-count-cassandra.pig
# check job running status in http://localhost:8088/

# check whether data is written to cassandra
# go to terminal that runs docker exec -it cassandra bash
SELECT COUNT(*) FROM tweet.tweetcount;
SELECT COUNT(*) FROM tweet.hashtagcount;
```

## Data Visualization

### Setup elasticsearch and kibana using docker containers
```sh
# start elasticsearch
docker run -d -p 9200:9200 -p 9300:9300 --name elasticsearch docker.elastic.co/elasticsearch/elasticsearch:6.0.0

# verify elasticsearch is running
curl http://localhost:9200/

# get ip address of the elasticsearch docker container
docker exec elasticsearch cat /etc/hosts

# start kibana
docker run -d -p 5601:5601 --name kibana -e ELASTICSEARCH_URL=http://172.17.0.6:9200 docker.elastic.co/kibana/kibana:6.0.0  # replace 172.17.0.6 with your ip address

# open http://localhost:5601/status to verify kibana is working
```

### Setup logstash

#### configure logstash to connect with elasticsearch
```sh
# first replace 172.17.0.6 with your elasticsearch docker container ip address in the files below:
# capstone/logstash/logstash.yml file, xpack.monitoring.elasticsearch.url: http://172.17.0.6:9200
# capstone/logstash/pipeline-redis/logstash.conf file,
# elasticsearch {
#    hosts => ["172.17.0.6:9200"]
#    ...
# }
# capstone/logstash/pipeline-tweetcount/logstash.conf file,
# elasticsearch {
#    hosts => ["172.17.0.6:9200"]
#    ...
# }
# capstone/logstash/pipeline-hashtagcount/logstash.conf file,
# elasticsearch {
#    hosts => ["172.17.0.6:9200"]
#    ...
# }
```

#### configure logstash to extract from Redis
```sh
# replace 172.17.0.5 with your redis docker container ip address in
# capstone/logstash/pipeline-redis/logstash.conf file,
# redis {
#    host => "172.17.0.5"
#    ...
# }
# find ip address of redis docker container
docker exec redis cat /etc/hosts

# start logstash
# please find the correct path of capstone/logstash/pipeline-redis/ in your local machine and use that instead
docker run --rm -it -v capstone/logstash/pipeline-redis/:/usr/share/logstash/pipeline/ -v capstone/logstash/logstash.yml:/usr/share/logstash/config/logstash.yml --name logstash-redis docker.elastic.co/logstash/logstash:6.0.0

# verify elasticsearch server is receiving data and indexing
curl 'localhost:9200/_cat/indices?v'
# look for index name tweet

# open http://localhost:5601/, create an index pattern in kinana,
# On the left sidebar, select Management Tab -> Index Patterns -> Create Index Pattern
# Fill in Index pattern: tweet
# Time Filter field name: @timestamp
# go to Discover tab, select the index name tweet, you should see some graph now
# Note: you may need to adjust Time Range accordingly
```

#### configure logstash to extract from Cassandra
```sh
# replace 172.17.0.2 with your cassandra docker container ip address in
# capstone/logstash/pipeline-tweetcount/logstash.conf file,
#  jdbc {
#    jdbc_connection_string => "jdbc:cassandra://172.17.0.2:9160/tweet"
#    ...
# }
# capstone/logstash/pipeline-hashtagcount/logstash.conf file,
#  jdbc {
#    jdbc_connection_string => "jdbc:cassandra://172.17.0.2:9160/tweet"
#    ...
# }
# find ip address of cassandra docker container
docker exec cassandra cat /etc/hosts

# start logstash
# please find the correct path of capstone/logstash/pipeline-tweetcount/ in your local machine and use that instead
docker run --rm -it -v capstone/logstash/pipeline-tweetcount/:/usr/share/logstash/pipeline/ -v capstone/logstash/logstash.yml:/usr/share/logstash/config/logstash.yml --name logstash-tweetcount docker.elastic.co/logstash/logstash:6.0.0

# verify elasticsearch server is receiving data and indexing
curl 'localhost:9200/_cat/indices?v'
# look for index name tweetcount

# open http://localhost:5601/, create an index pattern in kinana,
# On the left sidebar, select Management Tab -> Index Patterns -> Create Index Pattern
# Fill in Index pattern: tweetcount
# Time Filter field name: @timestamp
# go to Discover tab, select the index name tweetcount, you should see some graph now

# please find the correct path of capstone/logstash/pipeline-hashtagcount/ in your local machine and use that instead
docker run --rm -it -v capstone/logstash/pipeline-hashtagcount/:/usr/share/logstash/pipeline/ -v capstone/logstash/logstash.yml:/usr/share/logstash/config/logstash.yml --name logstash-hashtagcount docker.elastic.co/logstash/logstash:6.0.0

# verify elasticsearch server is receiving data and indexing
curl 'localhost:9200/_cat/indices?v'
# look for index name hashtagcount

# open http://localhost:5601/, create an index pattern in kinana,
# On the left sidebar, select Management Tab -> Index Patterns -> Create Index Pattern
# Fill in Index pattern: hashtagcount
# Time Filter field name: @timestamp
# go to Discover tab, select the index name hashtagcount, you should see some graph now
```

## Clean Data

### Extract Twitter entities
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

### Extract location
Extract place names from a URL or text

- [Geograpy](https://github.com/ushahidi/geograpy) - picked this one for now

- [geotext](https://github.com/elyase/geotext)

geograpy is more advanced and bigger in scope compared to geotext and can do everything geotext does. On the other hand geotext is leaner: has no external dependencies, is faster (re vs nltk) and also depends on libraries and data covered with more permissive licenses.