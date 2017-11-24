REGISTER /src/apache-cassandra-2.1.19/lib/apache-cassandra-2.1.19.jar;
REGISTER /src/apache-cassandra-2.1.19/lib/apache-cassandra-thrift-2.1.19.jar;
REGISTER /src/apache-cassandra-2.1.19/lib/libthrift-0.9.2.jar;
REGISTER /src/apache-cassandra-2.1.19/lib/jamm-0.3.0.jar;
REGISTER /src/apache-cassandra-2.1.19/lib/guava-16.0.jar;
REGISTER /src/apache-cassandra-2.1.19/lib/commons-lang3-3.1.jar;
REGISTER /src/metrics-core-3.0.2.jar;
REGISTER /src/cassandra-driver-core-2.0.9.2.jar;

DEFINE CqlStorage org.apache.cassandra.hadoop.pig.CqlNativeStorage();
a = LOAD 'cql://tweet/tweet' USING CqlStorage()
AS (
	unit_id: chararray,
 	name: chararray,
 	hashtags: chararray,
 	normalized_location: chararray,
 	tweet_count: long,
 	tweet_location: chararray,
 	tweet_text: chararray
 );

b = group a by normalized_location;
c = foreach b generate group AS tweet_location, SUM(a.tweet_count) AS tweet_count;
d = filter c by (tweet_location is not null and TRIM(tweet_location) != '');
dump d;

data_to_insert = FOREACH d GENERATE TOTUPLE(TOTUPLE('tweet_location', tweet_location)), TOTUPLE(tweet_count);
STORE data_to_insert INTO 'cql://tweet/tweetcount?output_query=UPDATE+tweet.tweetcount+SET+tweet_count+%3D+%3F+' USING CqlStorage();