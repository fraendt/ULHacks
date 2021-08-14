import asyncio
import logging
import math
import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands.errors import MissingRequiredArgument
from datetime import datetime, time, timedelta
import os
from dotenv import load_dotenv
import json

logging.basicConfig(level=logging.INFO)
load_dotenv()

sendTime = time(20, 46, 0)
#channel_id = 875954792319569974

client = Bot(command_prefix="!")

@client.command(name='embed', description='embed test', help='embed test')
async def embeded(ctx):
    embed=discord.Embed(title="top text",
                        description="bottom text",
                        color=0xFF5733)
    await ctx.send(embed=embed)

@client.command(name='echo', description='echo', help='echo')
async def echo(ctx, message=''):
    if message=='':
        return
    await ctx.send(message)

@client.command(name='where')
async def where(ctx):
    global w
    w=ctx
    await ctx.send(ctx.channel)

@client.command(name='anchor', description='send f5bot messages here', help = "Have the bot send messages to the channel !anchor was called in.")
async def anchor(ctx): # for lack of a better adjective
    channel_id = ctx.channel.id
    await ctx.send(channel_id)
    """if channel in anchors['']:
        await ctx.send('Channel already receiving all alerts.')
        return
    r = await confirmation(ctx, 'Are you sure you want to receive all alerts?')
    if r:
        anchors[''].append(channel)
        logging.info(str(channel)+' '+ctx.channel.__str__()+' has been anchored for all keywords.')
        await ctx.send('This channel will receive all alerts for all keywords.')
        return
    else:
        await ctx.send('Cancelled.')
        return"""

@client.command(name="settime", help = "Set time of the day at which a post is made (UTC). Enter in a 4 digit style (ex. 0428 = 4:28 AM UTC)")
async def settime(ctx, message=''):
    if message=='':
        return
    try:
        float(message)
    except:
        await ctx.send("Enter a number, dipshit.")
    else:
        message = int(message)
        sendTime = time(math.floor(message/100) % 24, message % 100,0)
        await ctx.send("Time set to " + sendTime.strftime("%H:%M"))


async def called_once_a_day(): 
    await bot.wait_until_ready() 
    channel = bot.get_channel(channel_id) 
    await channel.send("Hell yeah this works")

async def background_task():
    now = datetime.utcnow()
    if now.time() > WHEN:  
        tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0))
        seconds = (tomorrow - now).total_seconds()  # Seconds until tomorrow (midnight)
        await asyncio.sleep(seconds)   # Sleep until tomorrow and then the loop will start 
    while True:
        now = datetime.utcnow() 
        target_time = datetime.combine(now.date(), WHEN)
        seconds_until_target = (target_time - now).total_seconds()
        await asyncio.sleep(seconds_until_target)  # Sleep until we hit the target time
        await called_once_a_day()  # Call the helper function that sends the message
        tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0))
        seconds = (tomorrow - now).total_seconds()  # Seconds until tomorrow (midnight)
        await asyncio.sleep(seconds)   # Sleep until tomorrow and then the loop will start a new iteration







async def send_alert(keyword, ctx=None, **content):
    recipients = anchors['']
    try:
        recipients += anchors[keyword]
    except KeyError:
        pass
    if ctx:
        await ctx.send(**content)
    for recipient in recipients:
        await client.get_channel(recipient).send(**content)

async def confirmation(ctx, message):
    m = await ctx.send(message)
    yn = ['✅', '🚫']
    for i in yn:
        await m.add_reaction(i)
    try:
        reaction = await ctx.bot.wait_for('raw_reaction_add', timeout=30,
                                          check=lambda r: r.user_id == ctx.message.author.id and str(r.emoji) in yn and r.message_id == m.id)
    except asyncio.TimeoutError:
        await ctx.send('Timed out.')
        return False
    else:
        if str(reaction.emoji) == yn[0]:
            return True
        else:
            return False
    finally:
        try:
            await m.delete()
        except:
            pass
    await ctx.send(reaction)
    m.delete()

    
if __name__ == "__main__":
    client.loop.create_task(background_task())
    client.run(os.getenv('flimble'))
