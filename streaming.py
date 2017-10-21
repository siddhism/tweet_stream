# from __future__ import absolute_import, print_function

import json
import time
import os
from collections import Counter

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

consumer_key = os.environ.get('consumer_key')
consumer_secret = os.environ.get('consumer_secret')
access_token = os.environ.get('access_token')
access_token_secret = os.environ.get('access_token_secret')


if not consumer_key or not consumer_secret or not access_token or not access_token_secret:
    print 'Please set these environment variables in order to run \n',\
        'consumer_key, consumer_secret, access_token, access_token_secret \n',\
        'or contact siddhesh.it@gmail.com if keys are needed \n'


class Cache(object):

    def __init__(self):
        """
        word : count, last_seen
        """
        self.result = {}
        self.max_size = 10000
        self.start_time = time.time()
        self.step_time = 30  # should be 30
        self.last_cleanup = time.time()
        self.last_show_result = time.time()
        self.show_interval = 60  # shoud be 60
        self.last_prune = time.time()
        self.prune_interval = 200

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
            self.cleanup()
            self.last_cleanup = time.time()
        if time.time() >= self.last_show_result + self.show_interval:
            self.print_results()
            self.last_show_result = time.time()
        if time.time() >= self.last_prune + self.prune_interval:
            self.prune_cache()
            self.last_prune = time.time()

    def cleanup(self):
        """
        compute Every 30 seconds.
        If word does not appear in 1 minute decrememnt_count by 1
        If the count falls below zero, its pruned from cache
        """
        for word, data in self.result.items():
            count = data[0]
            last_seen = data[1]
            # every minute a word is not seen its score goes down by 1
            if last_seen <= time.time() - self.show_interval:
                count = count - 1
                # print ' decremented ', word, count
            self.result[word] = [count, time.time()]
            # if count falls below 0 pop it
            if count < 0:
                self.result.pop(word)

    def prune_cache(self):
        """
        if length of dict reaches maximum size. (not provided, assumed 1000)
        words with score zero can be dropped from cache.
        """
        if len(self.result.keys() == 1000):
            for word, data in self.result.items():
                count = data[0]
                if count == 0:
                    self.result.pop(word)

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
        self.cache = Cache()

    def on_data(self, data):
        data = json.loads(data)
        if data.get('text'):
            words = data.get('text').split(' ')
            self.cache.set_results(words)
        return True

    def on_error(self, status):
        print(status)
        self.cache.print_results()


if __name__ == '__main__':
    stdout_listener = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    stream = Stream(auth, stdout_listener)
    word = raw_input('press ctrl + c to exit anytime. Enter the word which you want to track : ')
    stream.filter(track=[word])
