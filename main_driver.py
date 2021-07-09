#!/usr/bin/env python3

import pprint
import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient
import bot_functions
import secret_info
import csv

TOKEN = secret_info.TOKEN
CHANNEL_ID = secret_info.CHANNEL_ID
COMMANDS = commands = f"My commands: \n **!mock [message]**: Mock a message \n **!sears**: See a tweet by {bot_functions.SEARS_DISCORD_USER_ID} \n **!dogs**: Get a cool dog fact! \n **!create @user**: Add someone (using their slack handle) to the cousin tier list \n **!upvote @user**: Add to someone's tier list points \n **!downvote @user**: Subtract from someone's tier list points \n **!tiers**: View the cousin tier list \n **!carl**: Get a certain carl quote \n **!stop**: Tell me to stop"
error_message_bad_command = "Command doesn't fit. You must acquit!"
error_message_did_something_wrong = "Oh my God, Nicole is killed? Oh my God, she is dead? The errors in your command killed her?"

def main():
    client = discord.Client()

    @client.event
    async def on_ready():
        channel = client.get_channel(CHANNEL_ID)
        await client.get_channel(CHANNEL_ID).send("Hey twitter world, this is yours truly.")
        print(f"{client.user} has connected to Discord.")


    @client.event
    async def on_message(message):

        # !mock command
        if message.content.lower().lower().startswith("!mock"):
            try:
                stripped_message = bot_functions.strip_command(message.content.lower(), "!mock")
                if len(stripped_message) == 0:
                    mocker =  message.author.id
                    mocked_message_buf_1 =  bot_functions.mock("My name is ")
                    mocked_message_buf_2 =  bot_functions.mock(" and I don't know how to use \'!mock\'")
                    mocker_format = "<@" + str(mocker) +">"
                    mocked_message_final = mocked_message_buf_1 + mocker_format + mocked_message_buf_2   
                    await message.channel.send(mocked_message_final)
                else:
                    mocked_message = bot_functions.mock(stripped_message)
                    await message.channel.send(mocked_message)
            except:
                await message.channel.send(error_message_did_something_wrong)
        
        # Sears tweet
        elif message.content.lower().startswith("!sears"):
            try:
                await message.channel.send(bot_functions.grab_sears_tweet())
            except:
                await message.channel.send(error_message_did_something_wrong)
        

        # Upvote a user
        elif message.content.lower().startswith("!upvote"):
            try:
                # Grab upvoter and upvoted info
                upvoted_id = message.mentions[0].id
                upvoter_id = message.author.id

            # Upvote and send message
                upvote_message = bot_functions.upvote_user(upvoted_id, upvoter_id)
                await message.channel.send(upvote_message)
            except:
                await message.channel.send(error_message_did_something_wrong)


        # Downvote a user
        elif message.content.lower().startswith("!downvote"):
            try:
                downvoted_id = message.mentions[0].id
                downvoter_id = message.author.id
                # Downvote and send message
                downvote_message = bot_functions.downvote_user(downvoted_id, downvoter_id)
                await message.channel.send(downvote_message)
            except:
                await message.channel.send(error_message_did_something_wrong)

        # Create member
        elif message.content.lower().startswith("!create"):
            try:
                user_to_create_id = message.mentions[0].id
                creator_id = message.author.id

                creation_message = bot_functions.create_user(user_to_create_id, creator_id)
                await message.channel.send(" " + creation_message)
            except:
                # user_to_create = message.content()[len("!create"):].strip()
                await message.channel.send("Who(m) do you want me to create?") 

        # Tier list
        elif message.content.lower().startswith("!tiers"):
            try:
                if not bot_functions.tier_list_is_up_to_date():
                    bot_functions.calc_tier_list()
                    await message.channel.send("Calculating Tier list...")
                tier_list = bot_functions.print_tier_list()
                tier_list = ''.join((line + '\n') for line in tier_list)
                await message.channel.send(tier_list)
            except:
                await message.channel.send(error_message_did_something_wrong)

        # Dogs killed by cops
        elif message.content.lower().startswith("!dogs_source") or message.content.lower().startswith("!dog_source"):
            try:
                await message.channel.send(bot_functions.dog_source())
            except:
                await message.channel.send(error_message_did_something_wrong)
        elif message.content.lower().startswith("!dogs"):
            try:
                await message.channel.send(bot_functions.dogs_killed())
            except:
                await message.channel.send(error_message_did_something_wrong)

        # Carl
        elif message.content.lower().startswith("!carl"):
            try:
                carl_quote = f"\"Hey Brian I'm done gassing up and heading out to the place at the other end of passbook just crossed Macgomery Road from Holbrook and just keep on going straight towards a house hot like you're going through Montgomery but on hospital road see\""
                await message.channel.send(carl_quote)
            except:
                await message.channel.send(error_message_did_something_wrong)
        
        # Stop
        elif message.content.lower().startswith("!stop"):
            try:
                video_link = "https://youtu.be/P4PgrY33-UA?t=42"
                await message.channel.send(video_link)
            except:
                await message.channel.send(error_message_did_something_wrong)

        # Help messages
        elif message.content.lower().startswith("!commands"):
            try:
                await message.channel.send(COMMANDS)
            except:
                await message.channel.send(error_message_did_something_wrong)
        elif message.content.lower().startswith("!help"):
            try:
                await message.channel.send("𝐆𝐨 𝐟𝐮𝐜𝐤 𝐲𝐨𝐮𝐫𝐬𝐞𝐥𝐟. \n\nᵗʳʸ \'!ᶜᵒᵐᵐᵃⁿᵈˢ\'")
            except:
                await message.channel.send(error_message_did_something_wrong)



        elif message.content.lower().startswith("!"):
            try:
                await message.channel.send(error_message_bad_command)
            except:
                await message.channel.send(error_message_did_something_wrong)
        


    client.run(TOKEN)

if __name__ == "__main__":
    main()