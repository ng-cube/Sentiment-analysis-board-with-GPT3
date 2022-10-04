import datetime

from googletrans import Translator
import time, datetime, re
import sqlConnectionClass, t5_summary

from config import *



class sentimentReasoning:
    # pull relevant constants from config file
    SENTIMENT_REASONING_LEN = SENTIMENT_REASONING_LEN
    SENTIMENT_REASONING_BOUNDS_LIST = (LOWER_SENTIMENT_RANGE, UPPER_SENTIMENT_RANGE)
    MIN_TWEET_LENGTH = MIN_TWEET_LENGTH

    def __init__(self):
        self.keyword_list = []
        self.sentiment_reasoning_tuples = []
        #self.sql_connection = sqlConnectionClass.sqlConnection()
        #self.sql_connection.create_connection() # connect to server


    def check_for_new_data(self):
        # control variable
        new_data_found = False

        sql_connection = sqlConnectionClass.sqlConnection()
        sql_connection.create_connection() # connect to server
        # fetch all available keywords
        [self.keyword_list.append(f_kw) \
        for f_kw in sql_connection.get_all_keywords() \
        if f_kw not in self.keyword_list]

        print(self.keyword_list)
        # check for each keyword if there is any missing sentimentReasoning
        for keyword in self.keyword_list:
            most_recent_ts_tweets = sql_connection.get_most_recent_ts(
                keyword=keyword,
                database="twitter_keyword",
            )
            oldest_ts_tweets = sql_connection.get_oldest_ts(
                keyword=keyword,
                database="twitter_keyword"
            )
            if most_recent_ts_tweets == None:
                continue # no tweets available for this keyword
            most_recent_ts_reasoning = sql_connection.get_most_recent_ts(
                keyword=keyword,
                database="twitter_sentiment_reasoning",
                column="end_timestamp",
            )


            if most_recent_ts_reasoning==None or most_recent_ts_tweets > (most_recent_ts_reasoning+self.SENTIMENT_REASONING_LEN):
                self.sentiment_reasoning_tuples.append(
                    (
                        keyword,
                        most_recent_ts_tweets,
                        most_recent_ts_reasoning,
                        oldest_ts_tweets
                    )
                )
                new_data_found = True # return to control unit

        sql_connection.close_connection()
        return new_data_found

    def update_all_sentiment_reasoning(self):
        # initialize t5 summary model
        t5 = t5_summary.t5()

        for keyword, tweet_ts, reasoning_ts, oldest_ts in self.sentiment_reasoning_tuples:
            #print(keyword)
            # iterate over the relevant timestamps
            if reasoning_ts != None:
                start_ts = reasoning_ts
            else:
                # if none available yet, set start to midnight before the first tweet ts
                start_ts = datetime.datetime.timestamp(
                    datetime.datetime.combine(
                        datetime.datetime.fromtimestamp(oldest_ts),
                        datetime.time.min
                    )
                )

            while start_ts <= tweet_ts:
                self._run_sentiment_reasoning_for_keyword(
                    keyword=keyword,
                    summary_model=t5,
                    start_ts=start_ts,
                    end_ts=start_ts+self.SENTIMENT_REASONING_LEN
                )
                start_ts += self.SENTIMENT_REASONING_LEN

    def _create_text_from_tweets(self, tweet_list):
        text = ""
        for tweet in tweet_list:
            text += tweet[:-1] + "."
        return text

    def _clean_and_translate_tweet(self, raw_tweet):
        translator = Translator()

        raw_tweet = re.sub("RT @\w+: ", " ", raw_tweet)
        #raw_tweet = re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", raw_tweet)
        raw_tweet = raw_tweet.replace("@", "")
        raw_tweet = re.sub(" +"," ",str(raw_tweet))
        raw_tweet = translator.translate(raw_tweet, dest="en").text
        #raw_tweet = raw_tweet.lower()

        return raw_tweet

    def _run_sentiment_reasoning_for_keyword(self, keyword, summary_model, start_ts, end_ts):
        return_dict = {}
        for sentiment_lower, sentiment_upper in self.SENTIMENT_REASONING_BOUNDS_LIST:
            sql_connection = sqlConnectionClass.sqlConnection()
            sql_connection.create_connection() # connect to server

            # get raw tweets

            tweet_list = sql_connection.load_batch_of_tweets(
                keyword=keyword,
                column="text", # preprocessed_text
                time_start=start_ts,
                time_end=end_ts,
                compound_min=sentiment_lower,
                compound_max=sentiment_upper,
                omitt_replies=True
            )
            tweet_list = [self._clean_and_translate_tweet(t) for t in tweet_list]

            print(keyword)

            # clean again?

            # create text from tweets
            tweet_text = self._create_text_from_tweets(tweet_list)
            print(tweet_text)
            if len(tweet_text) < 10:
                summary = "there are not enough tweets for a summary"
            else:
                summary = summary_model.summarize(tweet_text)
            return_dict[(sentiment_lower, sentiment_upper)] = summary

            # save the summary to sql
            #input(return_dict)
            sql_connection.update_sentiment_reasoning(
                keyword=keyword,
                update_dict=return_dict,
                start_ts=start_ts,
                end_ts=end_ts
            )
            return_dict = {}
            print("saved one")
            sql_connection.close_connection()
