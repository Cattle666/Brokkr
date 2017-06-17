#!/usr/bin/env python3

print('Begin Brokkr intialization sequence...')

import asyncio
import aiohttp
from collections import namedtuple
import datetime
import discord
from discord.ext.commands import Bot
from glob import glob
import random
import os
from os import path
import urllib.request
import urllib.parse
import re
from string import punctuation
import sys
import json


here = path.dirname(path.abspath(__file__))

# Add the parent directory of the directory this file is in to the system path
# so this folder is seen as a python package.
sys.path.append(path.dirname(here))

from Brokkr import secret

os.chdir(here)

brokkr = Bot(command_prefix='$')

# Used to define both commands and callbacks:
Responder = namedtuple('Responder', ('trigger', 'run'))

# Used to create fake messges that only contain a content attribute:
Message_stub = namedtuple('Message_stub', 'content')

repo_dir = '/srv/zandronum/wads'

trigger_prefix = r"(^| |[" + punctuation + r"])"
trigger_suffix = r"( |[" + punctuation + r"]|$)"


async def check_responder(responder, message):
    '''
    Checks if a given message should trigger a responder returning the response
    if so.
    '''

    if responder.trigger.search(message.content):
        return responder.run


async def cmd_hello(message):
    '''
    Says hello to the user.
    '''

    return 'Hello {0.author.mention}'.format(message)


async def cmd_help(message):
    return '''
        Greetings {0.author.mention} , here are the commands:
         ```$test``` = shows the amount of messages user has in a channel
         ```$sleep``` = puts the bot to sleep momentarily
         ```$hello``` = bot says hello to user
         ```$repo_wad``` = lists wads in VGP repository
         ```$repo_pk3``` = lists pk3s in the VGP repository
         ```$quit``` = Logs Brokkr out of the server
         ```$meow``` = posts a random rare cat pic
         ```$search``` = Search VGP repo for a game file
    '''.format(message)


async def cmd_meow(message):
    '''
    Random cat. Pulled from discord.py example.
    '''

    async with aiohttp.get('http://random.cat/meow') as r:
        if r.status == 200:
            js = await r.json()
            return js['file']
        else:
            return 'random cat service error {}'.format(r.status)


async def cmd_quit(message):
    await brokkr.logout()


async def cmd_repo_pk3(message):
    '''
    search the repository for pk3 files.  This can be achieved with $search
    *.pk3 instead and can be deprecated.
    '''

    return cmd_search(Message_stub('$search *.pk3'))


async def cmd_repo_wad(message):
    '''
    search the repository for wad files.  This can be achieved with $search
    *.wad instead and can be deprecated.
    '''

    return cmd_search(Message_stub('$search *.wad'))


async def cmd_search(message):
    '''
    Search VGP repository for specific game file.
    '''

    # remove extra whitespace and leading directory components that could lead
    # to directory traversal attacks:
    param = os.path.basename(message.content[8:].strip())
    # make the glob case insensitive:
    param = ''.join('[{}{}]'.format(c.upper(), c.lower()) if c.isalpha() else c for c in param)
    return file_search_report(file_search(repo_dir, param))



async def cmd_sleep(message):
    '''
    Causes the bot to become unresponsive for 5 seconds.
    '''

    await asyncio.sleep(5)
    await brokkr.send_message(message.channel, 'Done sleeping')


async def cmd_test(message):
    '''
    Pulled from discord.py example bot.
    '''

    counter = 0
    tmp = await brokkr.send_message(message.channel, 'Calculating messages...')
    async for log in brokkr.logs_from(message.channel, limit=100):
        if log.author == message.author:
            counter += 1

    await brokkr.edit_message(tmp, 'You have {} messages.'.format(counter))


def file_search(directory, query, recursive=True):
    '''
    Returns an iterable of file names in a directory ending with a given
    extension.
    '''

    cwd = os.getcwd()
    os.chdir(directory)
    results = glob(query, recursive=recursive)
    os.chdir(cwd)
    results.sort()
    return results


def file_search_report(results):
    if results:
        md_list = '\n'.join(map(lambda r: ' * ' + r, results))
        return '{} results found:\n' + md_list

    return 'no results found'


async def joinVoiceChannel():
    '''
    Example of simple script for bot to join specific voice channel
    ''' 

    channel = brokkr.get_channel(secret.voice_channel)
    voice = await brokkr.join_voice_channel(channel)
    print('Brokkr has joined Staff')


def make_callback(trigger, run):
    '''
    Creates an easy to use object for call/response matching.
    '''

    run_fn = run if callable(run) else lambda message: run
    trigger_re = ''.join((trigger_prefix, trigger, trigger_suffix))
    return Responder(trigger_re, run_fn)


def make_command(name, run):
    '''
    Creates an easy to use object for command handling.
    '''

    return Responder(re.compile(r'^' + name + r'($| .*)'), run)


responders = (
    make_callback('call of duty', 'Worst VG series ever BTW...'),
    make_callback('complex doom', 'Fuck Complex Doom!'),
    make_callback('cookie', 'What, you want a cookie!?'),
    make_callback('shit', 'fuck'),
    make_command('$hello', cmd_hello),
    make_command('$help', cmd_help),
    make_command('$meow', cmd_meow),
    make_command('$quit', cmd_quit),
    make_command('$repo_pk3', cmd_repo_pk3),
    make_command('$repo_wad', cmd_repo_wad),
    make_command('$search', cmd_search),
    make_command('$sleep', cmd_sleep),
    make_command('$test', cmd_test),
)


async def respond(message):
    if issubclass(message.__class, str):
        await brokkr.send_message(message.channel, message)
    else:
        # Mostly intended to handle Exceptions:
        await brokkr.send_message(message.channel, repr(message))


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


@brokkr.event
async def on_message(message):
    '''
    Called for every incomming message, looks for messages that should trigger
    some response from the bot.  The async code here could probably be further
    optimized by pipelining individual contexts instead of staging each part in
    the process.
    '''
    
    # The bot should completely ignore it's own messages:
    if message.author == brokkr.user:
        return

    # check which conditions have been triggered in paralell:
    _responders = (check_responder(r, message) for r in responders)

    # wait for all the checks to complete:
    _responders = asyncio.gather(*_responders, return_exceptions=True)

    # generate responses for the triggered conditions in parallel filtering out
    # the entries that returned None (by default) which do not need to run:
    responses = (run(message) for run in filter(callable, _responders))

    # wait for all responses to be compiled:
    responses = asyncio.gather(*responses, return_exceptions=True)

    # send out response messages in parallel filtering out those responses that
    # returned None by default (which probably managed the response itself):
    messages = (respond(message.channel, r) for r in filter(bool, responses))

    # wait for all responses to be sent out:
    messages = asyncio.gather(*messages, return_exceptions=True)

    errors = (err for err in messages if issubclass(err.__class__, Exception))
    if errors:
        pluralize = 's' if len(errors) > 1 else ''
        print('on_message response error{}:'.format(pluralize))
        print('\n'.join(repr(err) for err in errors))


@brokkr.event
async def on_ready():
    '''
    Completion of joining voice channel and backend identification...
    '''

    print('Logged in as:')
    print('Username: ' + brokkr.user.name)
    print('ID: ' + brokkr.user.id)
    print('------')
    await joinVoiceChannel()
    if not hasattr(brokkr, 'uptime'):
        brokkr.uptime = datetime.datetime.utcnow()


if __name__ == '__main__':
    brokkr.run(secret.token)

