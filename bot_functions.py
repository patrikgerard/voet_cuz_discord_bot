#!/usr/bin/env python3

import tweepy
import pprint
import datetime
import pytz
from random import randrange
import pymongo
from pymongo import MongoClient
from statistics import stdev

CONSUMER_KEY = "e2Hqw5TgDc8EUsA0RmP8XBJMj"
CONSUMER_SECRET_KEY = "5NxskZP7t46UfI6Gwi5hdrIbJRtX0NDmCEWtT1evAzFuoC3PNj"

ACCESS_TOKEN = "1345949283745411072-9vmNSqlxRSIPJ61qNVZv6Dko1vLNql"
ACCESS_TOKEN_SECRET = "KD6cbo7xColK3pps0wV4llYuex3BK8Fa7u1tqyTduxchr"

SEARS_TWITTER_USERNAME = "searysears"
SEARS_DISCORD_USER_ID = "<@610235781608374272>"

CONNECTION_URL = "mongodb+srv://patrikgerard:faPqJHzR8tARuS@cluster0.qv7sp.mongodb.net/test"

# Mocks message
def mock(message):
    index = True
    mocked_message = ""
    for letter in message:
        if index:
            mocked_message += letter.upper()
        else:
            mocked_message += letter.lower()
        if letter != ' ':
            index  = not index
    return mocked_message


# Strips only the leading whitespace
def strip_command(message, command):
    return message[len(command):].lstrip()


# grabs sears' timeline
def retrieve_timeline( api, user ):
    return api.user_timeline(screen_name = user, include_rts = True)

# grabs a sears tweet
def grab_sears_tweet():

    # create authenticator
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET_KEY)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    # create api object
    api = tweepy.API(auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True)

    # grab a tweet
    sears_tweets = retrieve_timeline(api, SEARS_TWITTER_USERNAME)
    number_of_tweets = len(sears_tweets)
    tweet = sears_tweets[randrange(number_of_tweets)]
    id = tweet._json['id']

    if "RT" in tweet._json['text']:
        text = api.get_status(id, tweet_mode = "extended").retweeted_status.full_text
        return f"This dickhead {SEARS_DISCORD_USER_ID} retweeted \"{text}\""
    else:
        text = api.get_status(id, tweet_mode = "extended")
        return f"{text.full_text}"

def create_user(user_to_create_id, creator_id=None):

    cluster = MongoClient(CONNECTION_URL)
    db = cluster["cousins"]
    collection = db["cousins_users"]

    if collection.count_documents({"_id": user_to_create_id}) > 0:
        if creator_id is None:
            return f"<@{user_to_create_is}> is already in rankings."
        else:
            down_vote_message = downvote_user(downvoted_id=creator_id)
            return f"<@{user_to_create_id}> is already in  cousin rankings. Minus one point for you <@{creator_id}>."

    post = {"_id": user_to_create_id,
     "points": 0,
     "tier": "B"
    }
    collection.insert_one(post)
    # add point to tier list date_checker
    # TODO: CALC TIER LIST AND TAKE POINT FROM DATE_CHECKER
    return f"<@{user_to_create_id}> added to cousin rankings."

# Upvotes a user
def upvote_user(upvoted_id, upvoter_id=None):
    if downvoted_id == None:
        return f"Who do you want me to upvote?"
    if upvoted_id == upvoter_id:
        return f"Go fuck yourself <@{upvoter_id}>."
    else:
        cluster = MongoClient(CONNECTION_URL)
        db = cluster["cousins"]
        collection = db["cousins_users"]

        # check that the user is in the database
        if collection.count_documents({"_id": upvoted_id}) != 1:
            user_created_message = create_user(user_to_create_id=upvoted_id)
            upvote_message = upvote_user(upvoted_id = upvoted_id)
            return f"<@{upvoted_id}> was created and upvoted."
        
        # Add a point and update the database
        query = {"_id": upvoted_id}
        user = collection.find(query)
        for result in user:
            points = result["points"]
        points += 1
        # add point to tier list date_checker
        collection.update_one({"_id":upvoted_id}, {"$set": {"points": points}}) 

        # TODO: CALC TIER LIST AND TAKE POINT FROM DATE_CHECKER

        return f"<@{upvoted_id}> was upvoted."

# Downvotes a User
def downvote_user(downvoted_id, downvoter_id=None):

    if downvoted_id == None:
        return f"Who do you want me to downvote?"
    if downvoted_id == downvoter_id:
        return f"Go love yourself <@{downvoter_id}>."
    else:
        cluster = MongoClient(CONNECTION_URL)
        db = cluster["cousins"]
        collection = db["cousins_users"]

        # check that the user is in the database
        if collection.count_documents({"_id": downvoted_id}) != 1:
            user_created_message = create_user(user_to_create_id=downvoted_id)
            downvote_message = downvote_user(downvoted_id = downvoted_id)
            return f"<@{downvoted_id}> was created and downvoted."
        
        # Add a point and update the database
        query = {"_id": downvoted_id}
        user = collection.find(query)
        for result in user:
            points = result["points"]
        points -= 1
        # add point to tier list date_checker
        collection.update_one({"_id":downvoted_id}, {"$set": {"points": points}}) 

        # TODO: CALC TIER LIST AND TAKE POINT FROM DATE_CHECKER

        return f"<@{downvoted_id}> was downvoted."

def calc_tier_list():
    # Get total score
    # Get average score
    # Get std dev
    cluster = MongoClient(CONNECTION_URL)
    db = cluster["cousins"]
    cousins_collection = db["cousins_users"]


    total_points = 0
    total_members = 0
    stdev_collector = [0]
    for member in list(cousins_collection.find({})):
        total_members += 1
        stdev_collector.append(member["points"])
        total_points += member["points"]

    average_points = total_points / total_members
    std_dev_points = stdev(stdev_collector)

    map_to_tier_list(total_points, average_points, std_dev_points)

    # Add each id to tier depending on their score
    # Add that tier to the id's "tier" attribute


def print_tier_list():
    # Loop through tier list


def tier_list_is_up_to_date():
    cluster = MongoClient(CONNECTION_URL)
    db = cluster["cousins"]
    update_needed_collection = db["update_info"]

    query = {"_id": "update_info"}
    info = update_needed_collection.find_one(query)
    print(info["update_needed"] == 0)
    return info["update_needed"] == 0




def map_to_tier_list(total_points, average_points, std_dev_points):
    tier_mapping =    { 
        'S' : round(average_points + (std_dev_points * 2)), # ge
        'A': round(average_points + (std_dev_points)), # ge
        'B': round(average_points), # ge
        'C': round(average_points - (std_dev_points)), # le 
        'D': round(average_points - (std_dev_points * 2)), # le
        'Piss Dungeon': round(average_points - (std_dev_points * 3)) # le
    }

    cluster = MongoClient(CONNECTION_URL)
    db = cluster["cousins"]
    collection_members = db["cousins_users"]
    collection_tier_list = db["tier_list"]
    collection_update_info = db["update_info"]
    for tier in tier_mapping:
        collection_tier_list.update_one({"_id":tier}, {"$set":{"members": []}})

    for member in list(collection_members.find({})):
        tier = ""
        if member["points"] >= tier_mapping['S']:
            tier = "S"
        elif member["points"] >= tier_mapping['A']:
            tier = "A"
        elif member["points"] >= tier_mapping['C']:
            tier = "B"
        elif member["points"] <= tier_mapping['C']:
            tier = "C"
        elif member["points"] <= tier_mapping['D']:
            tier = "D"
        else:
            tier = "Piss Dungeon"
        collection_tier_list.update_one({"_id":tier}, {"$push":{"members": member["_id"]}})
        collection_update_info.update_one({"_id": "update_info"}, {"$set": {"update_needed": 0}})
        collection_members.update_one({"_id":member["_id"]}, {"$set": {"tier": tier}})

        


