from cassandra.cluster import Cluster
from kafka import KafkaConsumer
from kafka.errors import KafkaError

import argparse
import atexit
import json
import logging
from kafka import KafkaConsumer

logger_format = '%(asctime)-15s %(message)s'
logging.basicConfig(format=logger_format)
logger = logging.getLogger('data-storage')
logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
	    # - setup command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('topic_name', help='the kafka topic to subscribe from')
    parser.add_argument('kafka_broker', help='the location of the kafka broker')
    parser.add_argument('key_space', help='the keyspace to use in cassandra')
    parser.add_argument('data_table', help='the data table to use')
    parser.add_argument('contact_points', help='the contact points for cassandra')

    logger.debug("hello")
    # - parse arguments
    args = parser.parse_args()
    logger.debug(args);
    topic_name = args.topic_name
    kafka_broker = args.kafka_broker
    key_space = args.key_space
    data_table = args.data_table
    contact_points = args.contact_points

    # - initiate a simple kafka consumer
    print type(topic_name)
    print type(kafka_broker)
    # consumer = KafkaConsumer(
    #     topic_name,
    #     bootstrap_servers=kafka_broker
    # )

    # for msg in consumer:
    #     logger.debug(msg)
    consumer = KafkaConsumer(topic_name,bootstrap_servers=kafka_broker)
    for msg in consumer:
        print(msg)