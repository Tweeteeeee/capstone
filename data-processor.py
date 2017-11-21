from cassandra.cluster import Cluster

import logging
import argparse

from ttp import ttp
import geograpy

logging.basicConfig()
logger = logging.getLogger('data-processor')
logger.setLevel(logging.DEBUG)

key_space = 'tweet'
data_table = 'tweet'
# - default cassandra nodes to connect
contact_points = '127.0.0.1'

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
        tags = ','.join(hashtags)
        logger.info('hashtags: %s', tags)

        user_mentions = parsed_entities.users
        mentions = ','.join(user_mentions)
        logger.info('mentions: %s', mentions)

        tweet_location = item.tweet_location
        logger.info('original tweet location: %s\n' % tweet_location)
        if tweet_location is None or not tweet_location:
            continue
        location = geograpy.get_place_context(text=tweet_location)

        regions = ''
        if location.regions is not None:
            regions = ','.join(location.regions)
        countries = ''
        if location.countries is not None:
            countries = ','.join(location.countries)
        cities = ''
        if location.cities is not None:
            cities = ','.join(location.cities)

        logger.info('normalized countries: %s\n' % countries)
        logger.info('normalized regions: %s\n' % regions)
        logger.info('normalized cities: %s\n' % cities)