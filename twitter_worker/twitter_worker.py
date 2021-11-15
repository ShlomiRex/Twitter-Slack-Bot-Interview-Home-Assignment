import ast
import configparser
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from requests_oauthlib import OAuth1

from dotenv import load_dotenv
import requests

# Logging
from requests.auth import HTTPBasicAuth

import slack_worker

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


def pull_tweets_last_hour(twitter_id):
    latest_tweets_datetime = datetime.now()
    latest_tweets_datetime -= timedelta(hours=1)

    return pull_tweets(twitter_id, start_time=latest_tweets_datetime)


def pull_tweets(twitter_id: str, start_time: datetime, max_results: int = 10):
    """
    Pulls tweets from a user by given start time.
    :param start_time:Datetime in UTC (important!)
    :param max_results: Maximum results to get. Minimum is 5.
    :param twitter_id:Username (Twitter ID)
    :return:List of tweets.
    """
    logger.info(f"Pulling tweets for {twitter_id} with start time: {start_time}")

    iso8601_date_format = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')

    params = {
        "max_results": max_results,
        "start_time": iso8601_date_format,
        "query": f"from:{twitter_id}"
    }

    res = requests.get(f"https://api.twitter.com/2/tweets/search/recent", headers=headers, params=params)

    if res.ok:
        return _process_tweets(res.json())
    else:
        logger.error(res.json())


def tweet(twitter_id: str, text: str) -> (bool, str):
    """
    Tweets a message onto the twitter platform.
    :param twitter_id: Is only used for logging. Will use environment tokens and API keys instead of this username.
    :param text: Message to post.
    :return:First parameter is success. If false, the second argument is the reason.
    """
    if text and len(text) > 0:
        logger.info(f"Tweeting: '{twitter_id}' with message: '{text}'")
        auth = OAuth1(os.environ["TWITTER_API_KEY"],
                      os.environ["TWITTER_API_KEY_SECRET"],
                      os.environ["TWITTER_ACCESS_TOKEN"],
                      os.environ["TWITTER_ACCESS_TOKEN_SECRET"])
        headers = {'Content-Type': 'application/json'}
        payload = {"text": text}
        res = requests.post("https://api.twitter.com/2/tweets", json=payload, auth=auth, headers=headers)
        return res.ok, res.text
    else:
        logger.info("Will not tweet empty message.")

