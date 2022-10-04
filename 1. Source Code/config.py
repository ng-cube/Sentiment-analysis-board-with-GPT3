# API keys
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAImPTQEAAAAAgD8Dcc38%2B%2F33CACnnvTibuI6ORM%3DKtypAUmVD9cqrS5C6zKEFdvYDQVIXH5kUsgaRTrnG1mczwaAhL"
CONSUMER_KEY = "fARQEx1xwr8FYiCA6buQLp0xT"
CONSUMER_SECRET = "WOQt6UVC7X53Ioh6rBUZ7SgzzYx0V7SbJquY9sgYJlQfw7zoUr"
ACCESS_TOKEN = "1181572972714303488-1bPwmIcRWWPL4k7hsYzvGZO1vQ9xSe"
ACCESS_TOKEN_SECRET = "QqLmkDk0rtro7zP63rNIYlPG2djnXpCo67zQCEEHMh1MC"

OPENAI_API_KEY = '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'

# sql related
SQL_DOMAIN = "cz2006.mysql.database.azure.com"#"sql6.freemysqlhosting.net"
SQL_USERNAME = "leon@cz2006"#"sql6482781"
SQL_PASSWORD = "SurelyNotABot55#"#"u3DrlcNLEa"



# ML constants
SENTIMENT_REASONING_LEN = 60*60*24
LOWER_SENTIMENT_RANGE = (-1, -0.25)
UPPER_SENTIMENT_RANGE = (0.25, 1)
MIN_TWEET_LENGTH = 10
T5_MAX_LEN = 16_384//2

# sql table names
DB_LIST = [
    "twitter_keyword",
    "twitter_sentiment_reasoning",
]


# twitter data translation for raw json
TWITTER_JSON_TRANS_DICT = {
    "language": ["lang"],
    "username": ["user", "screen_name"],
    "location": ["user", "location"],
    "description": ["user", "description"],
    "followers_count": ["user", "followers_count"],
    "friends_count": ["user", "friends_count"],
    "listed_count": ["user", "listed_count"],
    "favourites_count": ["user", "favourites_count"],
    "verified": ["user", "verified"],
    "statuses_count": ["user", "statuses_count"],

    "tweet_id": ["id"],#["entities", "media", 0, "url"],
    "is_quote_status": ["is_quote_status"],
    "in_reply_to_screen_name": ["in_reply_to_screen_name"],
    "retweet_count": ["retweet_count"],
    "favourite_count": ["favorite_count"],
}





SQL_TABLE_CONTENS = "CREATE TABLE IF NOT EXISTS twitter_keyword.{} (\n"+\
                    "item_id integer PRIMARY KEY AUTO_INCREMENT,\n"+\
                    "timestamp integer,\n"+\
                    "text TEXT,\n"+\
                    "language VARCHAR(25),\n"+\
                    "username VARCHAR(100),\n"+\
                    "location VARCHAR(100),\n"+\
                    "description TEXT,\n"+\
                    "followers_count integer,\n"+\
                    "friends_count integer,\n"+\
                    "listed_count integer,\n"+\
                    "favourites_count integer,\n"+\
                    "verified BINARY,\n"+\
                    "statuses_count integer,\n"+\
                    "is_quote_status BINARY,\n"+\
                    "in_reply_to_screen_name VARCHAR(100),\n"+\
                    "tweet_id VARCHAR(100),\n"+\
                    "retweet_count integer,\n"+\
                    "favourite_count integer,\n"+\
                    "preprocessed_text TEXT,\n"+\
                    "neg float,\n"+\
                    "neu float,\n"+\
                    "pos float,\n"+\
                    "compound float,\n"+\
                    "sentiment float,\n"+\
                    "polarity float,\n"+\
                    "subjectivity float);"

SQL_RESONING_TABLE_CONTENS = "CREATE TABLE IF NOT EXISTS twitter_sentiment_reasoning.{} (\n"+\
                            "reasoning_id integer PRIMARY KEY AUTO_INCREMENT,\n"+\
                            "start_timestamp float,\n"+\
                            "end_timestamp float,\n"+\
                            "start_sentiment float,\n"+\
                            "end_sentiment float,\n"+\
                            "summary TEXT);"

ADD_REASONING_BASE_COMMAND = "INSERT INTO twitter_sentiment_reasoning.{} "+\
    "(start_timestamp, end_timestamp, start_sentiment, end_sentiment, "+\
    "summary) VALUES(%s,%s,%s,%s,%s);"
