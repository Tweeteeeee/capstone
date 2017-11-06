from cassandra.cluster import Cluster

import logging
import argparse

from ttp import ttp

logging.basicConfig()
logger = logging.getLogger('data-processor')
logger.setLevel(logging.DEBUG)

key_space = 'tweet'
data_table = 'tweet'
# - default cassandra nodes to connect
contact_points = '127.0.0.1'

def list_to_str(input_list):
    result = ''
    is_first = True
    for item in input_list:
        if not is_first:
            result += ','
        result += item
        is_first = False
    return result

if __name__ == '__main__':
    # - setup command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('key_space', help='the keyspace to use in cassandra')
    parser.add_argument('data_table', help='the data table to use')
    parser.add_argument('contact_points', help='the contact points for cassandra')

    # - parse arguments
    args = parser.parse_args()
    key_space = args.key_space
    data_table = args.data_table
    contact_points = args.contact_points

    # - initiate a cassandra session
    cassandra_cluster = Cluster(
        contact_points=contact_points.split(',')
    )
    session = cassandra_cluster.connect()

    query_result = session.execute("SELECT * FROM %s.%s" % (key_space, data_table))
    parser = ttp.Parser()
    
    for item in query_result:
        tweet = item.tweet_text
        logger.info('original tweet text: %s\n' % tweet)
        if tweet is None:
            continue
        parsed_entities = parser.parse(tweet)
        hashtags = parsed_entities.tags
        tags = list_to_str(hashtags)
        logger.info('hashtags: %s', tags)

        user_mentions = parsed_entities.users
        mentions = list_to_str(user_mentions)
        logger.info('mentions: %s', mentions)

