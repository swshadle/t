#!/usr/bin/env python
# coding: utf-8

# %pip install tweepy


import tweepy
from datetime import datetime#, timezone
import pytz
import re

from secrets import Twitter_API_Key, Twitter_API_Secret_Key

tz = pytz.timezone('US/Central')

def age_of(tweet):
    duration = datetime.now(tz) - pytz.utc.localize(tweet.created_at, is_dst=None).astimezone(tz)
    seconds = duration.total_seconds()
    total_minutes = seconds // 60
    return int(total_minutes)

# Twitter_API_Key = 'HqkxLrdyFrwZemInMdsIqwoly'
# Twitter_API_Secret_Key = 'SZ9QbuEI1EE27m7n971QL89dO9AWAd77vgDqwJksAcFYq1IT8e'
# Twitter_Bearer_Token = 'AAAAAAAAAAAAAAAAAAAAAEwHLwEAAAAAA%2BYznSfSyZW8Er4CSyTzCL4HyKc%3D30id1qd2qlcYZY8peYTeyqk7jblTfhtdCTeOCKKs2ICqqhFs07'

consumer_key = Twitter_API_Key
consumer_secret = Twitter_API_Secret_Key

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

def get_breaking_news(age):
#     print('looking for news')
    screenname = 'nytimes'
    tweets = api.user_timeline(screenname, count=10)
    for tweet in tweets:
#         print(pytz.utc.localize(tweet.created_at, is_dst=None).astimezone(tz).strftime("%m/%d/%y %H:%M %p"), f'@{tweet.user.screen_name}', tweet.text, tweet.user.name)
        if 'Breaking News' in tweet.text:
            break
#     tweet = tweets[0]
#     print('1st try:', tweet.id, tweet.text)
    if age < age_of(tweet) or 'Breaking News' not in tweet.text:
#         print(pytz.utc.localize(tweet.created_at, is_dst=None).astimezone(tz).strftime("%m/%d/%y %H:%M %p"), f'@{tweet.user.screen_name}', tweet.text, tweet.user.name)
#         print('tweet was', age_of(tweet), 'minutes old')
        screenname = 'cnnbrk'
        tweet = api.user_timeline(screenname, count=1)[0]
#         print('2nd try:', tweet.id, tweet.text)
    status = api.get_status(tweet.id, tweet_mode="extended")
    try:
        full_text = status.retweeted_status.full_text
    except AttributeError:  # Not a Retweet
        full_text = status.full_text
    full_text = re.sub(r"http\S+", "", full_text).rstrip()
#     print(f'{tweet.id} {full_text} -{tweet.user.name} age: {age_of(tweet)}')
    if age >= age_of(tweet):
          return pytz.utc.localize(tweet.created_at, is_dst=None).astimezone(tz).strftime("%-l:%M%p ") + full_text, tweet.user.name, tweet.id
    else:
          return None, None, None


# # use example:
# text, name, tweet_id = get_breaking_news(15)
# if text or name:
#     print(text, '-', name)


# # screenname = 'cnnbrk'
# screenname = 'nytimes'
# tweets = api.user_timeline(screenname, count=1)
# tweet = tweets[0]
# tweetdate = pytz.utc.localize(tweet.created_at, is_dst=None).astimezone(tz)
# print(tweetdate.isoformat())
# print(tweetdate.strftime("%m/%d/%y %H:%M %p"))
# for tweet in tweets:
#     if 'Breaking News' in tweet.text:
#         print(pytz.utc.localize(tweet.created_at, is_dst=None).astimezone(tz).strftime("%m/%d/%y %H:%M %p"), f'@{tweet.user.screen_name}', tweet.text, tweet.user.name)
#         break
# tweet = tweets[0]
# print(tweet.text)

# def age_in_minutes(tweet):
#     duration = datetime.now(tz) - pytz.utc.localize(tweet.created_at, is_dst=None).astimezone(tz)
#     seconds = duration.total_seconds()
# #     hours = seconds // 3600
# #     minutes = (seconds % 3600) // 60
#     total_minutes = seconds // 60
# #     seconds = seconds % 60
# #     print(f'tweet is {int(hours)} hours, {int(minutes)} minutes, {int(seconds)} seconds old')
# #     print(f'tweet is {int(total_minutes)} total minutes old')
#     return int(total_minutes)

# print(f'latest tweet is {age_in_minutes(tweet)} minutes old')


if __name__ == "__main__":
    # Set up the display

    quote, person, tweet_id = get_breaking_news(300)
    print(quote, '-', person, tweet_id)
#     hash_display(quote, person, tweet_id)

