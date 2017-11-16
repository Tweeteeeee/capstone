# fetch tweet from file
# send data to kafka
# configurable kafka broker and kafka topic

from kafka import KafkaProducer

import csv
import json
# shutdown hook
import atexit
import argparse
import logging
import schedule
import time

import codecs
import sys
import io

from ttp import ttp
import geograpy

logging.basicConfig()
logger = logging.getLogger('data-producer')

# debug, info, warn, error
logger.setLevel(logging.DEBUG)

topic_name = ''
kafka_broker = ''
filename = "twitter-data.csv"
reload(sys)
# new-line character seen in unquoted field, so open file in universal-newline mode
data_file = io.open(filename, "rU", encoding='ISO-8859-1')
sys.setdefaultencoding('utf-8')
reader = csv.reader(data_file)
entity_parser = ttp.Parser()

def normalize_location(loc):
    if loc is None or not loc:
        return ''
    location = geograpy.get_place_context(text=loc)

    country = ''
    if location.countries is not None and len(location.countries) is not 0:
        country = location.countries[0]
    return country

def extract_hashtags(tweet):
    parsed_entities = entity_parser.parse(tweet)
    hashtags = parsed_entities.tags
    return hashtags

def fetch_tweet(producer):
    try:
        fields = next(reader)
        # logger.debug('read line: %s\n' % fields)
        tweet_location = fields[24]
        normalized_location = normalize_location(tweet_location)

        tweet_text = fields[19]
        hashtags = []
        try:
            hashtags = extract_hashtags(tweet_text)
        except UnicodeDecodeError:
            logger.info("tweet text: %s" % tweet_text)
        except Exception as e:
            logger.warn("Exception: %s" % e)

        data = {
            '_unit_id': fields[0],
            'gender': fields[5],
            'description': fields[10],
            'name': fields[14],
            'retweet_count': fields[17],
            'text': fields[19],
            'hashtags': hashtags,
            'tweet_coord': fields[20],
            'tweet_count': fields[21],
            'tweet_created': fields[22],
            'tweet_id': fields[23],
            'tweet_location': tweet_location,
            'normalized_location': normalized_location,
            'user_timezone': fields[25]
        }
        data = json.dumps(data)
        producer.send(topic=topic_name, value=data)
        logger.debug('sent data to kafka %s\n' % data)
    except EOFError as e:
        logger.warn('Reach EOF')
    except Exception as e:
        logger.warn('Failed to fetch tweet %s\n' % e)

def shutdown_hook(producer):
    logger.info('closing data file')
    data_file.close()
    logger.info('closing kafka producer')
    producer.flush(10)
    producer.close(10)
    logger.info('kafka producer closed')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('topic_name', help='the kafka topic to send to')
    parser.add_argument('kafka_broker', help='the kafka broker ip')

    # parse the argument
    args = parser.parse_args()
    topic_name = args.topic_name
    kafka_broker = args.kafka_broker

    producer = KafkaProducer(
        bootstrap_servers=kafka_broker
    )

    # skip the first line, headers
    next(reader)
    schedule.every(2).seconds.do(fetch_tweet, producer)

    atexit.register(shutdown_hook, producer)

    while True:
        schedule.run_pending()
        time.sleep(1)
