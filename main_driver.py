#!/usr/bin/env python3

import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient
import bot_functions


TOKEN = "ODU0Mzk4NjY3NDAyMzc5Mjk1.YMjWxA.P_GEnZo2E9zz98bwZ689zVUtPO4"

def main():
    client = discord.Client()

    @client.event
    async def on_ready():
        print(f"{client.user} has connected to Discord.")

    @client.event
    async def on_message(message):
        # !mock command
        if message.content.startswith("!mock"):
            stripped_message = bot_functions.strip_command(message.content, "!mock")
            mocked_message = bot_functions.mock(stripped_message)
            await message.channel.send(mocked_message)
        elif message.content.startswith("!sears"):
            await message.channel.send(bot_functions.grab_sears_tweet())

        elif message.content.startswith("!upvote"):
            try:
                # Grab upvoter and upvoted info
                upvoted_id = message.mentions[0].id
                upvoter_id = message.author.id

                # Upvote and send message
                upvote_message = bot_functions.upvote_user(upvoted_id, upvoter_id)
                await message.channel.send(upvote_message)
            except:
                await message.channel.send("Who(m) do you want me to upvote?") 
            
        elif message.content.startswith("!downvote"):
            # Grab downvoter and downupvoted info
            try:
                downvoted_id = message.mentions[0].id
                downvoter_id = message.author.id

                # Upvote and send message
                downvote_message = bot_functions.downvote_user(downvoted_id, downvoter_id)
                await message.channel.send(downvote_message)
            except:
                await message.channel.send("Who(m) do you want me to downvote?") 

        elif message.content.startswith("!create"):
            try:
                user_to_create_id = message.mentions[0].id
                creator_id = message.author.id

                creation_message = bot_functions.create_user(user_to_create_id, creator_id)
                await message.channel.send(creation_message)
            except:
                await message.channel.send("Who(m) do you want me to create?") 

        elif message.content.startswith("!calc"):
            bot_functions.print_tier_list()
        elif message.content.startwith("!tier_list"):
            if not bot_functions.tier_list_is_up_to_date():
                await message.channel.send("Calculating Tier list...")
                calc_tier_list()
            tier_list = print_tier_list()
            await message.channel.send(tier_list)

        elif message.content.startswith("!commands"):
            commands = "A list of my commands: \n !mock \n !sears"
            await message.channel.send(commands)



    client.run(TOKEN)

if __name__ == "__main__":
    main()