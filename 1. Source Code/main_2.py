from flask import *
import json, threading, random
import twitterConnectionClass, sqlConnectionClass, sentimentReasoningClass



class ExportingThread(threading.Thread):
    def __init__(self, keyword):
        self.keyword = keyword
        super().__init__()

    def run(self):
        self.tC = twitterConnectionClass.twitterConnection()
        self.tC.fetchTweetsForKeyword(keyword=self.keyword)


exporting_threads = {}
app = Flask(__name__)
app.debug = True

@app.route("/", methods=['GET'])
def summary():
    data_set = {
        "/estTime/?keyword=": "Estimate the time of pulling tweets for a specific keyword",
        "/runSentimentReasoning/": "Run the sentiment reasoning for all incomplete keywords",
        "/fetchTweets/?keyword=": "Fetch tweets for specific keyword and run sentiment reasoning",
        "/fetchTweets/progress/?thread_id=": "Check the progress of fetchTweets"
    }
    json_dump = json.dumps(data_set)
    return json_dump



@app.route("/estTime/", methods=['GET'])
def estimate_time():
    # /estTime/?keyword=YOUR_KEYWORD
    keyword = str(request.args.get('keyword'))

    # initialize db tables as necessary
    sC = sqlConnectionClass.sqlConnection()
    sC.create_connection()
    sC.initialize_all_dbs()
    sC.initialize_sql_database_table(keyword=keyword)


    # check time estimate
    tC = twitterConnectionClass.twitterConnection()
    time_est = tC.estimate_expected_time_of_pulling_tweets(keyword=keyword)


    data_set = {
        "Page": "estimateTime",
        "timeEstimate": time_est
    }
    json_dump = json.dumps(data_set)
    return json_dump


@app.route("/runSentimentReasoning/", methods=['GET'])
def run_sentiment_reasoning():
    print("updated")
    sent_reason = sentimentReasoningClass.sentimentReasoning()


    # call sentiment reasoning
    sent_reason.check_for_new_data()
    sent_reason.update_all_sentiment_reasoning()
    print("DONE")



@app.route("/fetchTweets/", methods=['GET'])
def fetch_tweets():
    global exporting_threads

    # /fetchTweets/?keyword=YOUR_KEYWORD
    keyword = str(request.args.get('keyword'))

    # initialize db tables as necessary
    sC = sqlConnectionClass.sqlConnection()
    sC.create_connection()
    sC.initialize_all_dbs()
    sC.initialize_sql_database_table(keyword=keyword)

    # fetch tweets
    thread_id = random.randint(0, 10_000)
    exporting_threads[thread_id] = ExportingThread(keyword)
    exporting_threads[thread_id].start()
    return 'task id: #%s' % thread_id

@app.route('/fetchTweets/progress/')
def progress():
    global exporting_threads
    thread_id = int(request.args.get("thread_id"))
    return str(exporting_threads[thread_id].tC.pct_progress)


@app.route('/getAllThreads/')
def oversight():
    global exporting_threads

    data_set = {}

    for thread_id in exporting_threads:
        # check if thread is done, and if so, terminate
        if thread_id not in exporting_threads or exporting_threads[thread_id].tC.done:
            # terminate thread
            del exporting_threads[thread_id]
    for thread_id in exporting_threads:
        data_set[thread_id] = {
            "keyword":exporting_threads[thread_id].keyword,
            "progress":str(exporting_threads[thread_id].tC.pct_progress)
        }
    json_dump = json.dumps(data_set)
    return json_dump


if __name__ == '__main__':
    app.run(port=7777)
