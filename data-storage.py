from cassandra.cluster import Cluster
from kafka import KafkaConsumer
from kafka.errors import KafkaError

import argparse
import atexit
import json
import logging

# - default kafka topic to read from
topic_name = 'tweet-analyzer'

# - default kafka broker location
kafka_broker = '127.0.0.1:9092'

# - default cassandra nodes to connect
contact_points = '192.168.99.101'

# - default keyspace to use
key_space = 'tweet'

# - default table to use
data_table = 'tweet'

logger_format = '%(asctime)-15s %(message)s'
logging.basicConfig(format=logger_format)
logger = logging.getLogger('data-storage')
logger.setLevel(logging.DEBUG)


def persist_data(tweet_data, cassandra_session):
    """
    persist tweet data into cassandra
    :param tweet_data:
        the tweet data looks like this:
        [{
            '_unit_id': fields[0],
            'gender': fields[5],
            'text': fields[19],
            'hashtags': hashtags
            'tweet_count': fields[21],
            'tweet_location': tweet_location,
            'normalized_location': normalized_location,
            'user_timezone': fields[25]
        }]
    :param cassandra_session:

    :return: None
    """
    try:
        logger.debug('Start to persist data to cassandra %s \n', tweet_data)
        parsed = json.loads(tweet_data)
        unit_id = str(parsed.get('_unit_id'))
        gender = parsed.get('gender')
        name = str(parsed.get('name'))
        tweet_text = str(parsed.get('text'))
        hashtags = str(parsed.get('hashtags'))
        tweet_count = parsed.get('tweet_count')
        tweet_location = parsed.get('tweet_location')
        normalized_location = parsed.get('normalized_location')
        user_timezone = parsed.get('user_timezone')

        # statement = "INSERT INTO %s (unit_id, name, tweet_text, tweet_location, normalized_location) VALUES ('%s', '%s', '%s', '%s', '$s')" % (data_table, unit_id, name, tweet_text, tweet_location, normalized_location)
        statement = cassandra_session.prepare("INSERT INTO %s (unit_id, name, tweet_text, hashtags, tweet_count, tweet_location, normalized_location) VALUES (?, ?, ?, ?, ?, ?, ?)" % data_table)
        cassandra_session.execute(statement, (unit_id, name, tweet_text, hashtags, tweet_count, tweet_location, normalized_location))
        logger.info('Persisted data to cassandra for unit_id: %s, name: %s, tweet_text: %s, hashtags: %s, tweet_count: %s, tweet_location: %s, normalized_location: %s\n' % (unit_id, name, tweet_text, hashtags, tweet_count, tweet_location, normalized_location))
    except Exception as e:
        logger.error('Failed to persist data to cassandra %s %s \n', tweet_data, e)


def shutdown_hook(consumer, session):
    """
    a shutdown hook to be called before the shutdown
    :param consumer: instance of a kafka consumer
    :param session: instance of a cassandra session
    :return: None
    """
    try:
        logger.info('Closing Kafka Consumer')
        consumer.close()
        logger.info('Kafka Consumer closed')
        logger.info('Closing Cassandra Session')
        session.shutdown()
        logger.info('Cassandra Session closed')
    except KafkaError as kafka_error:
        logger.warn('Failed to close Kafka Consumer, caused by: %s', kafka_error.message)
    finally:
        logger.info('Existing program')


if __name__ == '__main__':
    # - setup command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('topic_name', help='the kafka topic to subscribe from')
    parser.add_argument('kafka_broker', help='the location of the kafka broker')
    parser.add_argument('key_space', help='the keyspace to use in cassandra')
    parser.add_argument('data_table', help='the data table to use')
    parser.add_argument('contact_points', help='the contact points for cassandra')

    # - parse arguments
    args = parser.parse_args()
    logger.debug(args);
    topic_name = args.topic_name
    kafka_broker = args.kafka_broker
    key_space = args.key_space
    data_table = args.data_table
    contact_points = args.contact_points

    # - initiate a simple kafka consumer
    consumer = KafkaConsumer(
        topic_name,
        bootstrap_servers=kafka_broker
    )
        
    # - initiate a cassandra session
    cassandra_cluster = Cluster(
        contact_points=contact_points.split(',')
    )
    session = cassandra_cluster.connect()

    session.execute("DROP KEYSPACE IF EXISTS %s" % (key_space))
    session.execute("CREATE KEYSPACE IF NOT EXISTS %s WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '3'} AND durable_writes = 'true'" % key_space)
    session.set_keyspace(key_space)
    session.execute("CREATE TABLE IF NOT EXISTS %s (unit_id text, name text, tweet_text text, hashtags text, tweet_count text, tweet_location text, normalized_location text, PRIMARY KEY (unit_id, name))" % data_table)

    # - setup proper shutdown hook
    atexit.register(shutdown_hook, consumer, session)

    for msg in consumer:
        persist_data(msg.value, session)
