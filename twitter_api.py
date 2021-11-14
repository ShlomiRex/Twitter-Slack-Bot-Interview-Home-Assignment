import datetime
import logging
import os
from dataclasses import dataclass

import requests

logger = logging.getLogger()


@dataclass
class Tweet:
    id: int
    text: str


class TwitterAPI:
    def __init__(self):
        bearer = os.environ["TWITTER_BEARER_TOKEN"]
        self.headers = {
            "Authorization": f"Bearer {bearer}"
        }
        self.users = {}


    def _process_tweets(self, js: dict) -> [Tweet]:
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



    def pull_tweets_last_hour(self, page, max_results: int = 10):
        """
        Pulls tweets from a page(user) from the last hour.
        :param max_results: Maximum results to get.
        :param page:Username (Twitter ID)
        :return:JSON containing the tweets.
        """
        logger.info(f"Pulling tweets from last hour")

        latest_tweets_dateime = datetime.datetime.now()
        latest_tweets_dateime -= datetime.timedelta(hours=100)  # TODO: Change back to 1 hour. This is only for testing.

        iso8601_date_format = latest_tweets_dateime.strftime('%Y-%m-%dT%H:%M:%SZ')

        params = {
            "max_results": max_results,
            "start_time": str(iso8601_date_format),
            "query": f"from:{page}"
        }

        res = requests.get(f"https://api.twitter.com/2/tweets/search/recent", headers=self.headers, params=params)

        return self._process_tweets(res.json())
