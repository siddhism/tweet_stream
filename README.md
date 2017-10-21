# Tweet stream

----
> A package to track most used words around a word being tweeted live.

----
## Setup

Install requirements

    virtualenv env_temp_stream
    source env_temp_stream/bin/activate
    pip install -r requirements.txt

Get api keys from twitter

* Go to http://apps.twitter.com and create an app.
* The consumer key and secret will be generated for you after
* After the step above, you will be redirected to your app's page.
* Create an access token under the the "Your access token" section


Setup your twitter api keys as environment variables

    export consumer_key="your_consumer_key"
    export consumer_secret="your_consumer_secret"
    export access_token="your_access_token"
    export access_token_secret="your_access_token_secret"


Run

    python streaming.py 

Input the word which you want to track. it displays progress every minute about most used words from live stream around the input word.

press ctrl +C to exit the script anytime.
    
