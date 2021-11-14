import datetime
import logging
import os
import requests

logger = logging.getLogger()


class TwitterAPI:
    def __init__(self):
        bearer = os.environ["TWITTER_BEARER_TOKEN"]
        self.headers = {
            "Authorization": f"Bearer {bearer}"
        }
        self.users = {}

    def _get_id_from_username(self, username):
        if username in self.users:
            return self.users[username]
        try:
            res = requests.get(f"https://api.twitter.com/2/users/by/username/{username}", headers=self.headers)
            id = res.json().get("data").get("id")
            self.users[username] = id
            return id
        except Exception as e:
            logger.error(e)

    def pull_tweets_last_hour(self, page, max_results: int = 10):
        """
        Pulls tweets from a page(user) from the last hour.
        :param max_results: Maximum results to get.
        :param page:Username (Twitter ID)
        :return:JSON containing the tweets.
        """
        id = self._get_id_from_username(page)
        if id:
            latest_tweets_dateime = datetime.datetime.now()
            latest_tweets_dateime -= datetime.timedelta(hours=1)

            iso8601_date_format = latest_tweets_dateime.strftime('%Y-%m-%dT%H:%M:%SZ')

            params = {
                "max_results": max_results,
                "start_time": str(iso8601_date_format)
            }
            res = requests.get(f"https://api.twitter.com/2/users/{id}/tweets", headers=self.headers, params=params)
            return res.json()
