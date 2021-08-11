# bot.py
import os

import discord
from commands import *

with open("alfred-bot_token.txt") as bestand:
    TOKEN = bestand.readline()

client = discord.Client()
users_ready = []

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user or message.author.bot:
        return
    #Autoresponder voor fotos
    checker = check_for_txt2pic(message.content) #Function in commands.py
    if checker[0]: #If True
        channel = message.channel
        await channel.send(file=discord.File(checker[1]))

    #Branch voor alle @Alfred
    if len(message.mentions) != 0 and client.user in message.mentions:
        users_ready.append(message.author) #Add user to users_ready[] if @Alfred
        #MOET NOG NE CHECK BIJ
        print("Added user "+ str(message.author))
        #print("we got him")

    #Check bericht voor user in users_rdy[]
    if message.author in users_ready:
        #print("Content:\n" + message.content)
        execute = check_content(message) #Stuur message naar check_content en returned een discord executable
        print(str(execute))
        if execute is not None:
            await execute

client.run(TOKEN)