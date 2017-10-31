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

logging.basicConfig()
logger = logging.getLogger('data-producer')

# debug, info, warn, error
logger.setLevel(logging.DEBUG)

topic_name = ''
kafka_broker = ''
filename = "twitter-data.csv"
# new-line character seen in unquoted field, so open file in universal-newline mode
data_file = open(filename, "rU")
reader = csv.reader(data_file)

def fetch_tweet(producer):
	try:
		fields = next(reader)
		# logger.debug('read line: %s\n' % fields)
		data = {
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
