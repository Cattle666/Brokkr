#!/usr/bin/env python3

print("Begin Brokkr intialization sequence...")

import asyncio
import aiohttp
import datetime
import discord
from discord.ext.commands import Bot
import random
import os
from os import path
import urllib.request
import urllib.parse
import re
import string
import json

os.chdir(path.dirname(path.abspath(__file__)))

brokkr = Bot(command_prefix="$")

async def joinVoiceChannel():
'''Example of simple script for bot to join specific voice channel'''    
    channel = brokkr.get_channel('300631190002466818')
    voice = await brokkr.join_voice_channel(channel)
    print('Brokkr has joined Staff')

@brokkr.event
async def on_ready():
'''Completion of joining voice channel and backend identification...'''
    print('Logged in as:')
    print('Username: ' + brokkr.user.name)
    print('ID: ' + brokkr.user.id)
    print('------')
    await joinVoiceChannel()
    if not hasattr(brokkr, 'uptime'):
        brokkr.uptime = datetime.datetime.utcnow()

@brokkr.event
async def make_trigger(word):
    return r"(^| |[" + string.punctuation + "])" + word + r"( |[" + string.punctuation + "]|$)"
'''Work in progress. Call and response fun with specific terms.'''
@brokkr.event
async def cookie(self, message, match):
    await make_trigger("cookie")
    return 'What, you want a cookie!?'

@brokkr.event
async def complex_doom(self, message, match):
    await make_trigger("complex doom")
    return 'Fuck Complex Doom!'

@brokkr.event
async def call_of_duty(self, message, match):
    await make_trigger("call of duty")
    return 'Worst VG series ever BTW...'

@brokkr.event
async def shit(self, message, match):
    await make_trigger("shit")
    return 'fuck'

@brokkr.event
async def on_message(message):
'''Archaic help message. Could use some revision.'''
    if message.content.startswith('$help'):
        helpmsg = 'Greetings {0.author.mention} , here are the commands:\n```$test``` = shows the amount of messages user has in a channel\n ```$sleep``` = puts the bot to sleep momentarily\n ```$hello``` = bot says hello to user\n ```$repo_wad``` = lists wads in VGP repository\n ```$repo_pk3``` = lists pk3s in the VGP repository\n ```$quit``` = Logs Brokkr out of the server\n ```$meow``` = posts a random rare cat pic\n ```$search``` = Search VGP repo for a game file'.format(message)
        await brokkr.send_message(message.channel, helpmsg)

'''Pulled from discord.py example bot.'''
    if message.content.startswith('$test'):
        counter = 0
        tmp = await brokkr.send_message(message.channel, 'Calculating messages...')
        async for log in brokkr.logs_from(message.channel, limit=100):
            if log.author == message.author:
                counter += 1

        await brokkr.edit_message(tmp, 'You have {} messages.'.format(counter))
    
    elif message.content.startswith('$sleep'):
        await asyncio.sleep(5) 
        await brokkr.send_message(message.channel, 'Done sleeping')
    
    if message.author == brokkr.user:
        return

    if message.content.startswith('$hello'):
        msg = 'Hello {0.author.mention}'.format(message)
        await brokkr.send_message(message.channel, msg) 

    if message.content.startswith('$repo_wad'):
'''Displays all .wad files contained in the VGP repository'''
        for file in os.listdir("/srv/zandronum/wads/"):
            if file.endswith(".wad"):
                wads = os.path.join(file).format(message)
                await brokkr.send_message(message.channel, wads)    
    
    if message.content.startswith('$repo_pk3'):
'''Displays all .pk3 files contained in the VGP repository'''
        for file in os.listdir("/srv/zandronum/wads/"):
            if file.endswith(".pk3"):
                pk3s = os.path.join(file).format(message)
                await brokkr.send_message(message.channel, pk3s)

    if message.content.startswith('$meow'):
'''Random cat. Pulled from discord.py example'''
        async with aiohttp.get('http://random.cat/meow') as r:
            if r.status == 200:
                js = await r.json()
                await brokkr.send_message(message.channel, js['file'])

    if message.content.startswith('$search'):
'''Search VGP repository for specific game file.'''
        await brokkr.send_message(message.channel, 'Type $file [filename]')

        def check(msg):
            return msg.content.startswith('$file')

        message = await brokkr.wait_for_message(author=message.author, check=check)
        file_name = message.content[len('$file'):].strip()
        cur_dir = '/srv/zandronum/wads/'

        while True:
            file_list = os.listdir(cur_dir)
            parent_dir = os.path.dirname(cur_dir)
            if file_name in file_list:
                await brokkr.send_message(message.channel, "File Exists in repository")
                break
            else:
                if cur_dir == parent_dir: #if dir is root dir
                    await brokkr.send_message(message.channel, "File not found")
                    break
                else:
                    cur_dir = parent_dir
    if(message.content.startswith("$quit")):
        await brokkr.logout()
#Below is a bunch of WIP:
#
#@brokkr.listen()
#async def on_message(message):
#    print('one')
#
#brokkr.event
#async def on_message(message):    
#'''Random rare pepe post. Works! Must set up folder with pics internally.'''
#    if(message.content.startswith("~pepe")):
#        imgList = os.listdir("pepe")
#        imgString = random.choice(imgList)
#        path = "pepe/" + imgString
#        msg = await brokkr.send_file(message.channel, path)
#
#    if message.content.startswith('~yt'):
#        query_string = urllib.parse.urlencode({"search_query" : await brokkr.send_message(message.channel, input('What would you like to watch?'))})
#        msg = await brokkr.wait_for_message(author=message.author)
#        html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
#        search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
#        await brokkr.send_message(message.channel, ("http://www.youtube.com/watch?v=" + search_results[0]))
#
#    if message.content.startswith('~great'):
#        await brokkr.send_message(message.channel, 'Say something...')
#        msg = await brokkr.wait_for_message(author=message.author)
#        await brokkr.send_message(message.channel, 'Fuck you.')

brokkr.run("Bot Token")
