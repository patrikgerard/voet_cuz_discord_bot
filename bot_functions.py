#!/usr/bin/env python3

import asyncio
import tweepy
import pprint
from datetime import datetime, date
import pytz
from random import randrange
import pymongo
from pymongo import MongoClient
from statistics import stdev
import secret_info
import csv
import random
import time
import discord
import math
from PIL import Image, ImageFont, ImageDraw 
import textwrap

CONSUMER_KEY = secret_info.CONSUMER_KEY
CONSUMER_SECRET_KEY = secret_info.CONSUMER_SECRET_KEY

ACCESS_TOKEN = secret_info.ACCESS_TOKEN
ACCESS_TOKEN_SECRET = secret_info.ACCESS_TOKEN_SECRET 

SEARS_TWITTER_USERNAME = secret_info.SEARS_TWITTER_USERNAME
SEARS_DISCORD_USER_ID = secret_info.SEARS_DISCORD_USER_ID

CONNECTION_URL = secret_info.CONNECTION_URL

DOG_SOURCE = "https://www.criminallegalnews.org/news/2018/jun/16/doj-police-shooting-family-dogs-has-become-epidemic/"

INFORMATION_FILE_NAME ="information.txt"
ANNOY_MARK_FILE_NAME = "annoy_mark_mode.txt"
epoch = datetime(1970,1,1)
vote_refresh_time = 180 # 3 minutes
republican_voting_url = "https://rb.gy/wih8jw"
help_doc = "help.txt"
update_doc = "update_notes.txt"
intro_doc = "introduction.txt"
bee_facts_txt = "bee_facts.txt"
allowed_horny_permit_time = secret_info.allowed_horny_permit_time # one hour
horny_jail_sentence_time = secret_info.horny_jail_sentence_time # one hour
horny_choices = secret_info.horny_choices
# horny_jail_list = "horny_jail_list.txt"
horny_jail_messages = secret_info.horny_jail_messages
bonk_image = secret_info.bonk_image

horny_jail_role = secret_info.horny_jail_role

horny_check_cooldown = secret_info.horny_check_cooldown
permit_request_cooldown = secret_info.permit_request_cooldown
permit_request_chance = secret_info.permit_request_chance
horny_strike_cooldown = secret_info.horny_strike_cooldown

mom_statuses = secret_info.mom_statuses

r_join_file = secret_info.r_join_file
mp3_files = secret_info.mp3_files

async def free_from_horny_jail(channel, horndog, role, time_to_release):
    await asyncio.sleep(time_to_release)
    await horndog.remove_roles(role)
    await channel.send(f"Oh god hide the children <@{horndog.id}> is out of horny jail.")

async def remove_horny_strike_async(horny_offender, strikes_to_take, collection, cooldown_time):
    await asyncio.sleep(cooldown_time)
    take_horny_strikes(horny_offender, strikes_to_take, collection)

async def random_join(vchannel, chance, cooldown):
    while True:
        if len(vchannel.members) > 0 and check_rjoin_mode() is True:
            print("Attempting to join vc")
            if random.randint(0, 100) < chance:
                vc = await vchannel.connect()
                vc.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(random.choice(mp3_files)), volume=1.0))
                while vc.is_playing():
                    await asyncio.sleep(1)
                await asyncio.sleep(0.5)
                await vc.disconnect()
        await asyncio.sleep(cooldown)

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

def create_user(user_to_create_id, creator_id=None, name=""):

    cluster = MongoClient(CONNECTION_URL)
    db = cluster["cousins"]
    collection = db["cousins_users"]

    if collection.count_documents({"_id": user_to_create_id}) > 0:
        if creator_id is None:
            return f"<@{user_to_create_id}> is already in rankings."
        else:
            down_vote_message = downvote_user(downvoted_id=creator_id)
            return f"<@{user_to_create_id}> is already in  cousin rankings. Minus one point for you <@{creator_id}>."
    current_time = int(current_time_in_seconds())
    post = {"_id": user_to_create_id,
     "points": 0,
     "tier": "B",
     "most_recent_vote_time": 0,
     "last_user_voted_on": user_to_create_id,
     "is_horny_jailer": 0,
     "has_horny_permit": 0,
     "horny_permit_start_time": 0,
     "horny_warnings": 0,
     "horny_strikes": 0,
     "in_horny_jail": 0,
     "horny_jail_sentence_start_time": 0,
     "last_horny_check": 0,
     "last_permit_request": 0,
     "user_name": name
    }
    collection.insert_one(post)
    set_update_needed()
    # add point to tier list date_checker
    # TODO: CALC TIER LIST AND TAKE POINT FROM DATE_CHECKER
    return f"<@{user_to_create_id}> added to cousin rankings."

# Upvotes a user
async def upvote_user(channel, upvoted_id, upvoter_id=None, name=""):
    if upvoted_id == None:
        await channel.send(f"Who do you want me to upvote?")
    if upvoted_id == upvoter_id:
        await channel.send(f"Go fuck yourself <@{upvoter_id}>.")
    else:
        cluster = MongoClient(CONNECTION_URL)
        db = cluster["cousins"]
        collection = db["cousins_users"]

        # check that the user is in the database
        if collection.count_documents({"_id": upvoted_id}) != 1:
            user_created_message = create_user(user_to_create_id=upvoted_id, name=name)
            upvote_message = upvote_user(channel, upvoted_id = upvoted_id)
            await channel.send(f"<@{upvoted_id}> was created and upvoted.")
        
        if upvoter_id != None:
            # Get the time since last vote
            last_vote = collection.find_one({'_id':upvoter_id})['most_recent_vote_time']
            current_time = current_time_in_seconds()
            time_since_last_vote = get_time_since_last_vote(current_time, last_vote)

            # Get the last user voted on
            last_user_voted_on = collection.find_one({'_id':upvoter_id})['last_user_voted_on']

            # see if they can vote
            voting_right = can_user_vote(last_user_voted_on, upvoted_id, time_since_last_vote)
            if voting_right != True:
                await channel.send(f"Call me a Republican, because I\'m taking away your right to vote <@{upvoter_id}>.\n[Voting on the same person too quickly]")
            else:
                # Add a point and update the database
                points = collection.find_one({'_id':upvoted_id})['points']
                points += 1
                # add point to tier list date_checker
                set_update_needed()
                collection.update_one({"_id":upvoted_id}, {"$set": {"points": points}}) 
                set_vote_time_and_user(upvoted_id, upvoter_id)
                await channel.send(f"<@{upvoted_id}> was upvoted.")
        else:
            # Add a point and update the database
            points = collection.find_one({'_id':upvoted_id})['points']
            points += 1
            # add point to tier list date_checker
            set_update_needed()
            collection.update_one({"_id":upvoted_id}, {"$set": {"points": points}}) 
            set_vote_time_and_user(upvoted_id, upvoter_id)
            await channel.send(f"<@{upvoted_id}> was upvoted.")


# Downvotes a User
def downvote_user(downvoted_id, downvoter_id=None, name=" "):

    if downvoted_id == None:
        return f"Who do you want me to downvote?"
    if downvoted_id == downvoter_id:
        return f"Go love yourself <@{downvoter_id}>."
    else:
        cluster = MongoClient(CONNECTION_URL)
        db = cluster["cousins"]
        collection = db["cousins_users"]

        # Check if the account exists
        if collection.count_documents({"_id": downvoted_id}) != 1:
            user_created_message = create_user(user_to_create_id=downvoted_id, name=name)
            downvote_message = downvote_user(downvoted_id = downvoted_id)
            return f"<@{downvoted_id}> was created and downvoted"
        
        # Check if they can vote
        if downvoter_id != None:
            # Get the time since last vote
            last_vote = collection.find_one({'_id':downvoter_id})['most_recent_vote_time']
            current_time = current_time_in_seconds()
            time_since_last_vote = get_time_since_last_vote(current_time, last_vote)

            # Get the last user voted on
            last_user_voted_on = collection.find_one({'_id':downvoter_id})['last_user_voted_on']

            # see if they can vote
            voting_right = can_user_vote(last_user_voted_on, downvoted_id, time_since_last_vote)
            if voting_right != True:
                return f"Call me a Republican, because I\'m taking away your right to vote <@{downvoter_id}>.\n[Voting on the same person too quickly]"
        
        # check that the user is in the database

        
        # Add a point and update the database
        points = collection.find_one({'_id':downvoted_id})['points']
        points -= 1
        # add point to tier list date_checker
        set_update_needed()
        collection.update_one({"_id":downvoted_id}, {"$set": {"points": points}})
        set_vote_time_and_user(downvoted_id, downvoter_id)
        return f"<@{downvoted_id}> was downvoted"

def calc_tier_list():

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
    set_tier_up_to_date()
    # info_collection = db["update_info"]
    # info_collection.update_one({"_id":"update_info"}, {"$set": {"update_needed": 0}})


def print_tier_list():
    # Loop through tier list
    cluster = MongoClient(CONNECTION_URL)
    db = cluster["cousins"]
    collection_tier_list = db["tier_list"]

    for tier in collection_tier_list.find():
        yield f"__{tier['_id']} Tier:__"
        for member in tier['members']:
            yield f" \t**{member}** "
    pass

def print_help_message():
    lines = open(help_doc, encoding='utf-8').read().splitlines()
    for line in lines:
        yield line

def print_intro_message():
    lines = open(intro_doc, encoding='utf-8').read().splitlines()
    for line in lines:
        yield line

def set_tier_up_to_date():
    reader = csv.reader(open(INFORMATION_FILE_NAME))
    lines = list(reader)
    lines[1][0] = 0

    writer = csv.writer(open(INFORMATION_FILE_NAME, "w"))
    writer.writerows(lines)

def tier_list_is_up_to_date():
    with open (INFORMATION_FILE_NAME, 'r') as csv_file:
        line_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_file:
            if line_count == 0:
                line_count += 1
            else:
                return int(row[0]) == 0
    #             print(row[0])
    # cluster = MongoClient(CONNECTION_URL)
    # db = cluster["cousins"]
    # update_needed_collection = db["update_info"]

    # query = {"_id": "update_info"}
    # info = update_needed_collection.find_one(query)
    # return info["update_needed"] == 0


def set_update_needed():
    reader = csv.reader(open(INFORMATION_FILE_NAME))
    lines = list(reader)
    lines[1][0] = 1

    writer = csv.writer(open(INFORMATION_FILE_NAME, "w"))
    writer.writerows(lines)


def map_to_tier_list(total_points, average_points, std_dev_points):
    tier_mapping =    { 
        'S' : int(math.ceil(average_points + (std_dev_points))), # ge
        'A': round(average_points + (std_dev_points*0.4)), # ge
        'B': round(average_points), # ge
        'C': round(average_points - (std_dev_points*0.2)), # le 
        'D': round(average_points - (std_dev_points*0.4)), # le
        'Piss Dungeon': round(average_points - (std_dev_points)), # le
        'State of Florida': round(average_points - (std_dev_points*1.4)) # le
    }

    cluster = MongoClient(CONNECTION_URL)
    db = cluster["cousins"]
    collection_members = db["cousins_users"]
    collection_tier_list = db["tier_list"]
    # collection_update_info = db["update_info"]
    for tier in tier_mapping:
        collection_tier_list.update_one({"_id":tier}, {"$set":{"members": []}})
    print(round(average_points - (std_dev_points)))
    for member in list(collection_members.find({})):
        tier = ""
        if member["points"] >= tier_mapping['S']:
            tier = "S"
        elif member["points"] >= tier_mapping['A']:
            tier = "A"
        elif member["points"] >= tier_mapping['C']:
            tier = "B"
        elif member["points"] >= tier_mapping['D']:
            tier = "C"
        elif member["points"] >= tier_mapping['Piss Dungeon']:
            tier = "D"
        elif member["points"] >= tier_mapping['State of Florida']:
            tier = "Piss Dungeon"
        else: 
            tier = "State of Florida"
        # collection_tier_list.update_one({"_id":tier}, {"$push":{"members": member["_id"]}})
        collection_tier_list.update_one({"_id":tier}, {"$push":{"members": member['user_name']}})
        # collection_update_info.update_one({"_id": "update_info"}, {"$set": {"update_needed": 0}})
        collection_members.update_one({"_id":member["_id"]}, {"$set": {"tier": tier}})



# Check who is the most horny
def horny_check(members):
    random_member = random.choice(members)
    member_name = random_member.name
    member_id = random_member.id
    return member_id, member_name
    # member_names = [member.name for member in members]
    # return random.choice(member_names)

def horny_quote_generator(chosen_horndog):
    choice =  chosen_horndog
    return "Mirror, mirror on the wall — **" + choice + "** is the horniest of them all."

def dog_source():
    return f"{DOG_SOURCE}"

def dogs_killed():
    current_year = datetime(datetime.today().year, 1, 1)
    # current_year = date(datetime.today().year, 1, 1)
    current_date = datetime.today()
    
    #.strftime("%Y-%m-%d %I")
    
    # prev_date = datetime.strptime("2021-07-08 4","%Y-%m-%d %H")
    # delta_last_inquiry = current_date - prev_date
    # seconds_since_last_incquiry = delta_last_inquiry.seconds
    # dogs_killed_since_last_inquiry = round(seconds_since_last_incquiry/3600)

    seconds_since_year_start = (current_date - current_year).total_seconds() 
    dogs_killed_since_year_start = round(seconds_since_year_start/3600)

    dog_quotes = ["Ruff world!", "Talk about puppy love!", "Man's best friend! Pig\'s worst enemy!"]

    return f"There have been approximately {dogs_killed_since_year_start} dogs killed by cops this year. " + random.choice(dog_quotes) + "\n\nType \'!dogs_source\' for source."


def current_time_in_seconds():
    current_time = datetime.today()
    time =  (current_time - epoch).total_seconds()
    return time

def get_time_since_last_vote(current_time, last_vote):
    time = current_time - last_vote
    return int(time)

    
def can_user_vote(last_user_voted_on, current_user_voted_on, time_since_last_vote):
    if last_user_voted_on != current_user_voted_on:
        return True
    if (last_user_voted_on == current_user_voted_on) and  (time_since_last_vote <= vote_refresh_time):
        return False
    else:
        return True 

def set_vote_time_and_user(voted_id, voter_id):
    current_time = int(current_time_in_seconds())
    # time.sleep(10)
    second_time = int(current_time_in_seconds())
    cluster = MongoClient(CONNECTION_URL)
    db = cluster["cousins"]
    collection = db["cousins_users"]
    # print("current time: " + str(current_time))
    # time.sleep(10)
    if voter_id != None:
        collection.update_one({"_id":voter_id}, {"$set": {"last_user_voted_on":voted_id}})
        collection.update_one({"_id":voter_id}, {"$set": {"most_recent_vote_time": current_time}})
        vote_time = collection.find_one({'_id':voted_id})['most_recent_vote_time']
        # print(f"Set_vote_time_and_user: {vote_time}")
        # print(f"difference: {vote_time - current_time}")


def toggle_mark_mode():
    reader = csv.reader(open(ANNOY_MARK_FILE_NAME))
    lines = list(reader)
    if int(lines[1][0]) == 1:
        lines[1][0] = 0
    else:
        lines[1][0] = 1
    writer = csv.writer(open(ANNOY_MARK_FILE_NAME, "w"))
    writer.writerows(lines)

def check_mark_mode():
    with open (ANNOY_MARK_FILE_NAME, 'r') as csv_file:
        line_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_file:
            if line_count == 0:
                line_count += 1
            else:
                return int(row[0]) == 1


def toggle_rjoin_mode():
    reader = csv.reader(open(r_join_file))
    lines = list(reader)
    if int(lines[1][0]) == 1:
        lines[1][0] = 0
    else:
        lines[1][0] = 1
    writer = csv.writer(open(r_join_file, "w"))
    writer.writerows(lines)

def check_rjoin_mode():
    with open (r_join_file, 'r') as csv_file:
        line_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_file:
            if line_count == 0:
                line_count += 1
            else:
                return int(row[0]) == 1


def bee_facts():
    bee_facts = []
    lines = open(bee_facts_txt, encoding='utf-8').read().splitlines()
    # ojs_day.append([line for line in lines])
    for line in lines:
        bee_facts.append(line)
    return random.choice(bee_facts)

async def create_all_horny_info(list_mems_id, client):
    cluster = MongoClient(CONNECTION_URL)
    db = cluster["cousins"]
    my_collection = db["cousins_users"]
    attribute = "last_permit_request"
    for member in list_mems_id:
        namealmost = await client.fetch_user(member)
        real_name = namealmost.name
        my_collection.update_one({"_id":member}, {"$set": {"user_name": real_name}})


    # attributes = ["has_horny_permit", "horny_permit_start_time","horny_warnings","horny_strikes","in_horny_jail","horny_jail_sentence_start_time"]
    # # my_collection.update_many({}, {"$set": {"has_horny_permit": 0}}, upsert=False, array_filters=None)
    # for attribute in attributes:    
    #     my_collection.update_many({}, {"$set": {attribute: 0}}, upsert=False, array_filters=None)
    

# horny warning config
def has_horny_warning(horny_offender):
    cluster = MongoClient(CONNECTION_URL)
    db = cluster["cousins"]
    collection = db["cousins_users"]
    horny_warning = collection.find_one({'_id':horny_offender})['horny_warnings']
    return horny_warning == 1

def give_horny_warning(horny_offender, collection):
    # cluster = MongoClient(CONNECTION_URL)
    # db = cluster["cousins"]
    # collection = db["cousins_users"]
    collection.update_one({"_id":horny_offender}, {"$set": {"horny_warnings": 1}}) 

def take_horny_warning(horny_offender, collection):
    # cluster = MongoClient(CONNECTION_URL)
    # db = cluster["cousins"]
    # collection = db["cousins_users"]
    collection.update_one({"_id":horny_offender}, {"$set": {"horny_warnings": 0}})

# Horny strikes config
def horny_strikes_count(horny_offender):
    cluster = MongoClient(CONNECTION_URL)
    db = cluster["cousins"]
    collection = db["cousins_users"]
    return collection.find_one({'_id':horny_offender})['horny_strikes']

def give_horny_strike(horny_offender, collection):
    # cluster = MongoClient(CONNECTION_URL)
    # db = cluster["cousins"]
    # collection = db["cousins_users"]
    horny_strikes = collection.find_one({'_id':horny_offender})['horny_strikes']
    collection.update_one({"_id":horny_offender}, {"$set": {"horny_strikes": horny_strikes + 1}})
    asyncio.create_task(remove_horny_strike_async(horny_offender, 1, collection, horny_strike_cooldown))

def take_horny_strikes(horny_offender, strikes_to_take, collection):
    # cluster = MongoClient(CONNECTION_URL)
    # db = cluster["cousins"]
    # collection = db["cousins_users"]
    horny_strikes = collection.find_one({'_id':horny_offender})['horny_strikes']
    collection.update_one({"_id":horny_offender}, {"$set": {"horny_strikes": horny_strikes - strikes_to_take}})

# horny permit config
def has_valid_horny_permit(horny_offender):
    cluster = MongoClient(CONNECTION_URL)
    db = cluster["cousins"]
    collection = db["cousins_users"]
    horny_permit = collection.find_one({'_id':horny_offender})['has_horny_permit']
    horny_permit_time = collection.find_one({'_id':horny_offender})['horny_permit_start_time']

    current_time = current_time_in_seconds()
    time_since_permit_given = get_time_since_last(current_time, horny_permit_time)

    return horny_permit == 1 and time_since_permit_given <= allowed_horny_permit_time


def get_time_since_last(current_time, last_time):
    time = current_time - last_time
    return int(time)


def take_horny_permit(horny_offender):
    cluster = MongoClient(CONNECTION_URL)
    db = cluster["cousins"]
    collection = db["cousins_users"]
    collection.update_one({"_id":horny_offender}, {"$set": {"has_horny_permit": 0}})

# Horny jail config
def send_to_horny_jail(horny_offender, collection):
    current_time = int(current_time_in_seconds())
    # cluster = MongoClient(CONNECTION_URL)
    # db = cluster["cousins"]
    # collection = db["cousins_users"]
    collection.update_one({"_id":horny_offender}, {"$set": {"in_horny_jail": 1}})
    collection.update_one({"_id":horny_offender}, {"$set": {"horny_jail_sentence_start_time": current_time}})
    take_horny_strikes(horny_offender, 2, collection)
    take_horny_warning(horny_offender, collection)

def is_in_jail(horny_offender):
    current_time = int(current_time_in_seconds())
    cluster = MongoClient(CONNECTION_URL)
    db = cluster["cousins"]
    collection = db["cousins_users"]
    in_horny_jail = collection.find_one({'_id':horny_offender})['in_horny_jail']
    horny_jail_time = collection.find_one({'_id':horny_offender})['horny_jail_sentence_start_time']

    current_time = current_time_in_seconds()
    time_in_jail = get_time_since_last(current_time, horny_jail_time)
    return in_horny_jail == 1 and time_in_jail <= horny_jail_sentence_time

async def free_from_jail_immediate(channel, horny_offender):
    cluster = MongoClient(CONNECTION_URL)
    db = cluster["cousins"]
    collection = db["cousins_users"]
    collection.update_one({"_id":horny_offender}, {"$set": {"in_horny_jail": 0}})
    horny_jail_role_ = discord.utils.get(channel.guild.roles, name="In Horny Jail")
    horndog_member = channel.guild.get_member(horny_offender)
    await horndog_member.remove_roles(horny_jail_role_)
    await channel.send(f"Oh god hide the children <@{horny_offender}> is out of horny jail.")


# def give_horny_strike_or_warning_or_jail(horny_offender):
#     cluster = MongoClient(CONNECTION_URL)
#     db = cluster["cousins"]
#     collection = db["cousins_users"]
#     # if the offender is in horny jail
#     if is_in_jail(horny_offender):
#         return f"<@{horny_offender}> is already in horny jail."
#     # otherwise, if the offender has a permit
#     elif has_valid_horny_permit(horny_offender):
#         return f"Not to worry. <@{horny_offender}> has a permit to be this horny."
#     # if the offender has a horny warning
#     elif has_horny_warning(horny_offender) == False:
#         give_horny_warning(horny_offender, collection)
#         return f"<@{horny_offender}> was given a warning for execessive horniness."
#     elif horny_strikes_count(horny_offender) < 2:
#         give_horny_strike(horny_offender, collection)
#         return f"<@{horny_offender}> was given a horny strike."
#     # if the horny offender already has 2 horny strikes, send them to jail upon the third
#     elif horny_strikes_count(horny_offender) >= 2:
#         send_to_horny_jail(horny_offender, collection)
#         return f"Go to horny jail <@{horny_offender}>."

async def give_horny_strike_or_warning_or_jail(channel, horny_offender, horny_offender_name):
    cluster = MongoClient(CONNECTION_URL)
    db = cluster["cousins"]
    collection = db["cousins_users"]
    if horny_cooldown_check(horny_offender) is True:
        await channel.send(f"**{horny_offender_name}** was given temporary horny amnesty. Quit asking and maybe <@{horny_offender}> will calm down.")
    # if the offender is in horny jail
    elif is_in_jail(horny_offender):
        await channel.send(f"**{horny_offender_name}** is already in horny jail. Give **{horny_offender_name}** some alone-time for self-fellatio")
        set_horny_cool_down(channel, horny_offender)
    # otherwise, if the offender has a permit
    elif has_valid_horny_permit(horny_offender):
        await channel.send(f"Not to worry. **{horny_offender_name}** has a permit to be this horny.")
        set_horny_cool_down(channel, horny_offender)
    # if the offender has a horny warning
    elif has_horny_warning(horny_offender) == False:
        give_horny_warning(horny_offender, collection)
        await channel.send(f"**{horny_offender_name}** was given a warning for execessive horniness.")
        set_horny_cool_down(channel, horny_offender)
    elif horny_strikes_count(horny_offender) < 2:
        give_horny_strike(horny_offender, collection)
        await channel.send(f"**{horny_offender_name}** was given a horny strike.")
        set_horny_cool_down(channel, horny_offender)
    # if the horny offender already has 2 horny strikes, send them to jail upon the third
    elif horny_strikes_count(horny_offender) >= 2:
        send_to_horny_jail(horny_offender, collection)
        await channel.send(f"Go to horny jail **{horny_offender_name}**.")
        horny_jail_role_ = discord.utils.get(channel.guild.roles, name="In Horny Jail")
        horndog_member = channel.guild.get_member(horny_offender)
        await horndog_member.add_roles(horny_jail_role_)
        await channel.send(bonk_image)
        asyncio.create_task(free_from_horny_jail(channel, horndog_member, horny_jail_role_, horny_jail_sentence_time))


def is_horny():
    return random.choice(list(horny_choices))

def horny_jail_message(horndog):
    horny_message = f"{random.choice(horny_jail_messages)} <@{horndog}>.\n" 
    return horny_message

async def print_jail(channel):
    role = discord.utils.get(channel.guild.roles, name=horny_jail_role)
    horny_jail_text = f"𝐇𝐎𝐑𝐍𝐘 𝐉𝐀𝐈𝐋:\n"
    for member in channel.members:
        if role in member.roles:
            horny_jail_text += f"<@{member.id}>\n"
    await channel.send(horny_jail_text)

def horny_cooldown_check(horny_offender):
    cluster = MongoClient(CONNECTION_URL)
    db = cluster["cousins"]
    collection = db["cousins_users"]
    horny_check_time = collection.find_one({'_id':horny_offender})['last_horny_check']

    current_time = current_time_in_seconds()
    time_since_poked = get_time_since_last(current_time, horny_check_time)

    return time_since_poked <= horny_check_cooldown

def set_horny_cool_down(channel, horny_offender):
    cluster = MongoClient(CONNECTION_URL)
    db = cluster["cousins"]
    collection = db["cousins_users"]
    current_time = current_time_in_seconds()
    collection.update_one({"_id":horny_offender}, {"$set": {"last_horny_check": current_time}}) 


def permit_request_time_check(asker):
    cluster = MongoClient(CONNECTION_URL)
    db = cluster["cousins"]
    collection = db["cousins_users"]
    request_time = collection.find_one({'_id':asker})['last_permit_request']

    current_time = current_time_in_seconds()
    time_since_asked = get_time_since_last(current_time, request_time)

    return time_since_asked >= permit_request_cooldown

async def give_horny_permit(channel, asker):
    cluster = MongoClient(CONNECTION_URL)
    db = cluster["cousins"]
    collection = db["cousins_users"]
    if permit_request_time_check(asker) is True:
        if random.randint(0, 100) < permit_request_chance:
            current_time = int(current_time_in_seconds())
            collection.update_one({"_id":asker}, {"$set": {"has_horny_permit": 1}})
            collection.update_one({"_id":asker}, {"$set": {"horny_permit_start_time": current_time}})
            await channel.send(f"You have my permission to be horny for just a little bit <@{asker}>.")
            collection.update_one({"_id":asker}, {"$set": {"last_permit_request": current_time}})
        else:
            await channel.send(f"No permit for you, sinner <@{asker}>.")
            await channel.send(f"{downvote_user(asker)} for unluckiness")
            current_time = int(current_time_in_seconds())
            collection.update_one({"_id":asker}, {"$set": {"last_permit_request": current_time}})
    else:
        await channel.send(f"No permit for you, sinner <@{asker}>.")
        await channel.send(f"{downvote_user(asker)} for impatience")
        current_time = int(current_time_in_seconds())
        collection.update_one({"_id":asker}, {"$set": {"last_permit_request": current_time}})

async def print_update_notes(channel):
    lines = open(update_doc, encoding='utf-8').read().splitlines()
    update_message = ""
    for line in lines:
        update_message += line + "\n"
    await channel.send(update_message)

async def image_on_text(channel, text):
    image = Image.open("images/computer_buff_guy_1.jpg")
    title_font = ImageFont.truetype("Go-Bold.ttf", 30)
    title_text = text
    image_editable = ImageDraw.Draw(image)
    image_len = 383

    line_width = 42
    margin = 10
    if len(text) >= 400:
        offset = image_len*0.1
        title_font = ImageFont.truetype("Go-Bold.ttf", 20)
        line_width = 65
    elif len(text) >= 300:
        offset = image_len*0.33
        title_font = ImageFont.truetype("Go-Bold.ttf", 25)
        line_width = 52
        if len(text) <= 350:
            offset = image_len*0.4
    elif len(text) >= 200:
        offset = image_len*0.5
    else:
        offset = image_len*0.6

    for line in textwrap.wrap(title_text, width=line_width):
        image_editable.text((margin, offset), line, font=title_font, fill="#ffffff")
        offset += title_font.getsize(line)[1]
    image.save("images/result.jpg")
    await channel.send(file=discord.File("images/result.jpg"))