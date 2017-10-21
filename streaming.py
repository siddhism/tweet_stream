# from __future__ import absolute_import, print_function

import json
import time
from collections import Counter

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

# Go to http://apps.twitter.com and create an app.
# The consumer key and secret will be generated for you after
# TODO : move them to env variables
consumer_key = "14loJxKN3k9FtJDC8Q4mmBrGA"
consumer_secret = "oLkx6lXScnZGSE4nlKv6e0tOTMYtx5bidZnbtdaFPGTSLUvVrt"

# After the step above, you will be redirected to your app's page.
# Create an access token under the the "Your access token" section
access_token = "2422424420-MKnQbC39ThGQh8O5An5t12JUGuPrqTeGJG2HOXQ"
access_token_secret = "6PyJDrw8ilepeSeFc745Gp0pI4qaCfd8X7xxOLas4Fyki"


class Result(object):

    def __init__(self):
        """
        word : count, last_seen
        """
        self.result = {}
        self.max_size = 10000
        self.start_time = time.time()
        self.step_time = 5 # should be 30
        self.last_cleanup = time.time()
        self.last_show_result = time.time()
        self.show_interval = 10 # shoud be 60
        pass

    def set_results(self, words):
        """
        Every 30 seconds, if a word appears
        if word does not exists already set count to 1
        if word exists, increment count by 1
        """
        for word in words:
            if word in self.result.keys():
                self.result[word] = [self.result[word][0] + 1, time.time()]
            else:
                self.result[word] = [1, time.time()]
        if time.time() >= self.last_cleanup + self.step_time:
            print 'calling cleanup'
            self.cleanup()
            self.last_cleanup = time.time()
        if time.time() >= self.last_show_result + self.show_interval:
            self.print_results()
            self.last_show_result = time.time()

    def cleanup(self):
        """
        compute Every 30 seconds, if word does not appear in 1 minute, decrememnt_count by 1
        if the count falls below zero, its pruned from cache
        """
        print time.time()
        print 'doing cleanup'
        for word, data in self.result.items():
            count = data[0]
            last_seen = data[1]
            # every minute a word is not seen its score goes down by 1
            if last_seen <= time.time() - self.show_interval:
                count = count - 1
                print ' decremented ', word, count
            self.result[word] = [count, time.time()]
            # if count falls below 0 pop it
            if count < 0:
                self.result.pop(word)
        pass

    def prune_cache(self):
        """
        if length of dict reaches maximum size. (not provided, assumed 10k)
        words with score zero can be dropped from cache.
        """

    def print_results(self):
        """
        After starting, print results at an interval of 1 minute.
        words which have cache score > 1
        """
        data = {k: v[0] for k, v in self.result.items()}
        counted_values = Counter(data).most_common()
        for word, count in counted_values:
            if count > 1:
                print word, 'appeared ', count, ' times.'


class StdOutListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    This is a basic listener that just prints received tweets to stdout.

    """
    def __init__(self, *args, **kwargs):
        super(StdOutListener, self).__init__(*args, **kwargs)
        self.result = Result()

    def on_data(self, data):
        print time.time()
        data = json.loads(data)
        # assuming data is single tweet here
        if data.get('text'):
            words = data.get('text').split(' ')
            self.result.set_results(words)
        return True

    def on_error(self, status):
        print(status)
        self.result.print_results()


if __name__ == '__main__':
    stdout_listener = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    stream = Stream(auth, stdout_listener)
    word = raw_input('press ctrl + c to exit anytime. Enter the word which you want to track : ')
    stream.filter(track=[word])
