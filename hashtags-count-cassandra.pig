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
	unit_id: long,
 	name: chararray,
 	hashtags: chararray,
 	normalized_location: chararray,
 	tweet_count: long,
 	tweet_location: chararray,
 	tweet_text: chararray
 );

words = FOREACH a GENERATE FLATTEN(TOKENIZE(REPLACE(hashtags, '[\\[\\]]', ''), ',')) AS word;
grouped = group words by word;
wordcount = foreach grouped generate group, COUNT(words) AS count;
ordered = order wordcount by count DESC;
top20 = limit ordered 20;
dump top20;