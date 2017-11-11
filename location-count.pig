REGISTER piggybank.jar;
a = load 'twitter-data-cleaned.csv' USING org.apache.pig.piggybank.storage.CSVExcelStorage() AS (f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13,f14,f15,f16,f17,f18,f19,f20,f21,f22:long,f23,f24,f25,f26,f27);
b = foreach a generate $26 as tweet_location, $21 as tweet_count;
c = group b by tweet_location;
d foreach c generate group, SUM(b.tweet_count);
dump d;
