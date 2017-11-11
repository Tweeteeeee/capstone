----tweetdata = LOAD 'cql://tweet' USING CqlNativeStorage();
a = load 'twitter-data-cleaned.csv' using PigStorage() as (name:chararray, text:chararray,hashtags:chararray,tweet_count:int);
b = foreach a generate flatten(TOKENIZE(text))as word;
c = group b by word;
d = foreach c generate COUNT(b), group;
dump d;
