import ast
import configparser
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests

# Logging
logger = logging.getLogger()

# Configuration files, environ
load_dotenv()
config = configparser.ConfigParser()
config.read("config.ini")

# Globals
pages_to_pull = config["TWITTER"]["pages"]
headers = {"Authorization": f"Bearer {os.environ['TWITTER_BEARER_TOKEN']}"}
pages_to_pull = ast.literal_eval(pages_to_pull)  # Convert string that represents list, to python list type


@dataclass
class Tweet:
    id: int
    text: str


def _process_tweets(js: dict) -> [Tweet]:
    """
    Process the json of the API response.
    :param js: Dictionary which can contain data and metadata.
    :return: List of tweets.
    """
    logger.debug("Processing tweets")
    result_count = 0
    if "meta" in js:
        if "result_count" in js["meta"]:
            result_count = js["meta"]["result_count"]

    if result_count == 0:
        return []

    res = []
    if "data" in js:
        for tweet in js["data"]:
            t = Tweet(tweet["id"], tweet["text"])
            res.append(t)
    return res


def pull_tweets_last_hour(twitter_id, max_results: int = 10):
    """
    Pulls tweets from a page(user) from the last hour.
    :param max_results: Maximum results to get. Minimum is 5.
    :param twitter_id:Username (Twitter ID)
    :return:JSON containing the tweets.
    """
    logger.info(f"Pulling tweets from last hour for page: {twitter_id}")

    latest_tweets_datetime = datetime.now()
    latest_tweets_datetime -= timedelta(hours=100)  # TODO: Change back to 1 hour. This is only for testing.

    iso8601_date_format = latest_tweets_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')

    params = {
        "max_results": max_results,
        "start_time": str(iso8601_date_format),
        "query": f"from:{twitter_id}"
    }

    res = requests.get(f"https://api.twitter.com/2/tweets/search/recent", headers=headers, params=params)

    return _process_tweets(res.json())

def pull_new_tweets(twitter_username: str):
    return None