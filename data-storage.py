from cassandra.cluster import Cluster
from kafka import KafkaConsumer
from kafka.errors import KafkaError

import argparse
import atexit
import json
import logging

# - default kafka topic to read from
topic_name = 'twitter-analyzer'

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
			'description': fields[10],
			'name': fields[14],
			'retweet_count': fields[17],
			'text': fields[19],
			'tweet_coord': fields[20],
			'tweet_count': fields[21],
			'tweet_created': fields[22],
			'tweet_id': fields[23],
			'tweet_location': fields[24],
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
        description = str(parsed.get('description'))
        name = str(parsed.get('name'))
        retweet_count = parsed.get('retweet_count')
        tweet_text = str(parsed.get('text'))
        tweet_coord = parsed.get('tweet_coord')
        tweet_count = parsed.get('tweet_count')
        tweet_created = parsed.get('tweet_created')
        tweet_id = str(parsed.get('tweet_id'))
        tweet_location = parsed.get('tweet_location')
        user_timezone = parsed.get('user_timezone')

        statement = "INSERT INTO %s (unit_id, name, description ) VALUES ('%s', '%s', '%s')" % (data_table, unit_id, name, description)
        cassandra_session.execute(statement)
        logger.info('Persisted data to cassandra for unit_id: %s, name: %s, description: %s \n' % (unit_id, name, description))
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
    consumer = KafkaConsumer(
        topic_name,
        bootstrap_servers=kafka_broker
    )
        
    # - initiate a cassandra session
    cassandra_cluster = Cluster(
        contact_points=contact_points.split(',')
    )
    session = cassandra_cluster.connect()


    session.execute("CREATE KEYSPACE IF NOT EXISTS %s WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '3'} AND durable_writes = 'true'" % key_space)
    session.set_keyspace(key_space)
    session.execute("DROP TABLE %s" % data_table)
    session.execute("CREATE TABLE IF NOT EXISTS %s (unit_id text, name text, description text, PRIMARY KEY (unit_id, name))" % data_table)

    # - setup proper shutdown hook
    atexit.register(shutdown_hook, consumer, session)

    for msg in consumer:
        persist_data(msg.value, session)