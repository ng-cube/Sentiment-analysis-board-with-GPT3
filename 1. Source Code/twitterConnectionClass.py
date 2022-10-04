import numpy as np

import tweepy, time, datetime, re
from googletrans import Translator

from textblob import TextBlob
from nltk.sentiment.vader import SentimentIntensityAnalyzer

import sqlConnectionClass, sentimentReasoningClass
from config import *




class twitterConnection:
    # get all relevant API keys from config.py
    CONSUMER_KEY = CONSUMER_KEY
    CONSUMER_SECRET = CONSUMER_SECRET
    ACCESS_TOKEN = ACCESS_TOKEN
    ACCESS_TOKEN_SECRET = ACCESS_TOKEN_SECRET

    def __init__(self):
        # authenticate the connection
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        self.api = tweepy.API(
            auth,
            wait_on_rate_limit=True,
        )

        # create a twitter connection
        self.sql_connection = sqlConnectionClass.sqlConnection()
        self.sql_connection.create_connection()

        self.sent_reason = sentimentReasoningClass.sentimentReasoning()


    def estimate_expected_time_of_pulling_tweets(self, keyword):
        # get the first page
        tweet_pages = tweepy.Cursor(self.api.search, q=keyword, tweet_mode="extended", count=100).pages()
        end_ts = self.sql_connection.get_most_recent_ts(
                keyword=keyword
        )
        for page in tweet_pages:
            nr_tweets = len(page)
            first_ts = self.tweet_to_dict(
                tweet_status_object=page[0]
            )["timestamp"]

            last_ts = self.tweet_to_dict(
                tweet_status_object=page[-1]
            )["timestamp"]
            break

        # estimate the time it will take
        if nr_tweets < 100:
            expected_time = 0
        else:
            # project time interval fetched to whole week to estimate the number
            # of tweets there are in total
            time_frame = first_ts-last_ts # diff in sec
            if end_ts == None:
                stop_seconds = 60*60*24*7
            else:
                stop_seconds = first_ts-end_ts

            estimated_number_of_tweets = stop_seconds / time_frame
            # 900 per 15 min
            expected_time = ((15*60)/900) * estimated_number_of_tweets
        return expected_time

    def fetchTweetsForKeyword(self, keyword):#, end_ts=None):
        """
        Fetch all tweets that contain a specific keyword up to a specific
        timestamp (in case this is not the first time they are being pulled)
        """
        self.done = False
        return_list = []
        tweet_pages = tweepy.Cursor(self.api.search, q=keyword, tweet_mode="extended", count=100).pages()
        end_ts = self.sql_connection.get_most_recent_ts(
                keyword=keyword
        )
        try:
            self.current_ts = 0
            self.pct_progress = 0
            internal_done = False
            #input(len(tweet_pages))
            for i,tweets_page in enumerate(tweet_pages): # iterate over the various pages
                for ii, tweet in enumerate(tweets_page):

                    # preprocess the tweet
                    processed_tweet_dict = self.tweet_to_dict(
                        tweet_status_object=tweet
                    )

                    if end_ts != None and processed_tweet_dict["timestamp"] <= end_ts:
                        internal_done = True

                    print(f"Page nr:\t{i}\t\tTweet nr:\t{ii}" +\
                            f"\t\t{processed_tweet_dict['timestamp']} "+\
                            f"// {end_ts} // {len(return_list)}",
                             end="\r")
                    self.current_ts = processed_tweet_dict['timestamp']
                    if end_ts != None:
                        self.pct_progress = (time.time()-self.current_ts) / (time.time() - end_ts)
                    else:
                        self.pct_progress = (time.time()-self.current_ts)/ (60*60*24*7)

                    # clip the progress bar
                    self.pct_progress = np.clip(self.pct_progress, 0, 0.99)



                    return_list.append(processed_tweet_dict)

                    if len(return_list) >= 1_000:
                        self.sql_connection.update_tweet_batch(
                                keyword=keyword,
                                tweet_list=self.basic_sentiment_analysis(return_list),
                                database="twitter_keyword"
                            )
                        return_list = []


                    if internal_done:
                        break
                if internal_done:
                    break
        except Exception as exc:
            self.done = True
            print(f"UNEXPECTED exception when pulling tweets: {exc}")

        self.sql_connection.update_tweet_batch(
                keyword=keyword,
                tweet_list=self.basic_sentiment_analysis(return_list),
                database="twitter_keyword"
            )

        # call sentiment reasoning
        self.sent_reason.check_for_new_data()
        self.sent_reason.update_all_sentiment_reasoning()
        self.done = True


    def tweet_to_dict(self, tweet_status_object, remove_emoji=True):
        """
        Convert the raw returned json into a processed dictionary.
        """
        try:
            text = tweet_status_object._json["full_text"]
        except AttributeError:
            text = tweet_status_object.text

        return_dict = {
            "timestamp":self.convert_to_ts(tweet_status_object._json["created_at"]),
            "text":text
        }

        for key in TWITTER_JSON_TRANS_DICT.keys(): # taken from config.py
            return_dict[key] =  self.find_recursive_sub_key(
                twitter_json=tweet_status_object._json,
                key_list=TWITTER_JSON_TRANS_DICT[key]
            )

        return_dict["preprocessed_text"] = self.clean_and_translate_tweet(text)
        return return_dict

    def find_recursive_sub_key(self, twitter_json, key_list):
        """
        Recursively iterate over the different depths of the dictionary to
        find the pre-defined piece of information.
        """
        if len(key_list) == 1:
            return twitter_json[key_list[0]]
        else:
            return self.find_recursive_sub_key(
                        twitter_json=twitter_json[key_list[0]],
                        key_list=key_list[1:]
                    )

    def convert_to_ts(self, twitter_date):
        """ Twitter format: Sun Sep 05 02:53:56 +0000 2021 """
        return time.mktime(datetime.datetime.strptime(twitter_date,"%a %b %d %H:%M:%S +%f %Y").timetuple())


    def clean_and_translate_tweet(self, raw_tweet):
        """
        First clean the raw_tweet by removing unnecessary symbold and characters
        and then translate the tweet via the googletrans api.
        """
        translator = Translator()

        raw_tweet = re.sub("RT @\w+: ", " ", raw_tweet)
        raw_tweet = re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", raw_tweet)
        raw_tweet = re.sub(" +"," ",str(raw_tweet))
        raw_tweet = translator.translate(raw_tweet, dest="en").text
        raw_tweet = raw_tweet.lower()

        return raw_tweet


    def basic_sentiment_analysis(self, tweet_list):
        for sub_dict_num in range(len(tweet_list)):
            polarity, subjectivity = TextBlob(tweet_list[sub_dict_num]["preprocessed_text"]).sentiment
            score = SentimentIntensityAnalyzer().polarity_scores(tweet_list[sub_dict_num]["preprocessed_text"])

            tweet_list[sub_dict_num]["neg"] = score["neg"]
            tweet_list[sub_dict_num]["neu"] = score["neu"]
            tweet_list[sub_dict_num]["pos"] = score["pos"]
            tweet_list[sub_dict_num]["compound"] = score["compound"]
            tweet_list[sub_dict_num]["sentiment"] = int(np.argmax([score["neg"], score["neu"], score["pos"]])-1)
            tweet_list[sub_dict_num]["polarity"] = polarity
            tweet_list[sub_dict_num]["subjectivity"] = subjectivity

        return tweet_list



    ### Sentiment Reasoning sub-functions
