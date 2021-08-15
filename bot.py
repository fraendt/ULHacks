import asyncio
import logging
import math
import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot
from discord.ext.commands.errors import MissingRequiredArgument
from datetime import datetime, time, timedelta
import os
from dotenv import load_dotenv
import json
import scraper

logging.basicConfig(level=logging.INFO)
load_dotenv()
sendTime = time(23, 55, 0)
channel_id = 875954792319569974
TIMERS = {}

client = Bot(command_prefix="!")

# @client.command(name='embed', description='embed test', help='embed test')
async def embeded(ctx):
    embed=discord.Embed(title="top text",
                        description="bottom text",
                        color=0xFF5733)
    await ctx.send(embed=embed)

# @client.command(name='echo', description='echo', help='echo')
async def echo(ctx, message=''):
    if message=='':
        return
    await ctx.send(message)

# @client.command(name='where')
async def where(ctx):
    global w
    w=ctx
    await ctx.send(ctx.channel)

class Timer:
    def __init__(self, ctx, fx):
        self.ctx = ctx
        self.fx = fx
        self.task = None
    async def start(self):
        sleep_coro = asyncio.sleep(self.delay)
        task = asyncio.ensure_future(sleep_coro)
        # print('waiting')
        self.task = task
        try:
            await task
        except asyncio.CancelledError:
            return 
        await self.fx(self.ctx)

        self.running = True
        while self.running:
            try:
                await self.wait(self.recur)
            except asyncio.CancelledError:
                break
    def end(self):
        self.running = False
        self.stop()
    def schedule(self, delay, recur):
        self.stop()
        self.recur = recur
        self.delay = delay
        # print(recur, delay)
        return self
    async def wait(self, delay):
        sleep_coro = asyncio.sleep(delay)
        task = asyncio.ensure_future(sleep_coro)
        self.task = task
        try:
            await task
            return await self.fx(self.ctx)
        except asyncio.CancelledError:
            return 
    def stop(self):
        if self.task is not None:
            self.task.cancel()
            self.running = False

@client.command(name='anchor', description='subcribe current channel to wikihow articles', help = "Have the bot send messages to the channel !anchor was called in.")
async def anchor(ctx, start_time=None, interval="24h"): # for lack of a better adjective
    channel_id = ctx.channel.id
    timer = Timer(ctx.channel.id, called_once_a_day)
    timer.schedule(0, 24*60*60)
    TIMERS[channel_id] = timer
    await ctx.send("This channel has been subscribed to the Daily Dose of Discord.")
    await timer.start()

@client.command(name='unanchor', description='unsubcribe current channel to wikihow articles', help = "Unsubscribe a subscribed channel")
async def unanchor(ctx, start_time=None, interval="24h"): # for lack of a better adjective
    channel_id = ctx.channel.id
    if channel_id not in TIMERS.keys():
        return await ctx.send("This channel is not subscribed to the Daily Dose of Discord.")
    if not await confirmation(ctx, f"Are you sure you want to unsubscribe from Daily Dose of Discord?"):
        return await ctx.send("Cancelled unsubscription.")

    TIMERS.pop(channel_id).stop()
    await ctx.send("This channel has been unsubscribed from the Daily Dose of Discord.")

@client.command(name="settime", help = "Set time of the day at which a post is made (UTC). Enter in a HH:MM digit style (ex. 04:28 = 4:28 AM UTC)")
async def settime(ctx, message='', interval=86400):
    if message=='':
        return
    if ctx.channel.id not in TIMERS.keys():
        await ctx.send("This channel is not subscribed to the Daily Dose of Discord bot. Use !anchor to subscribe this channel to recieve daily articles.")
        return
    hour, minute = [int(i) for i in message.split(":")]
    if minute > 60 or hour >= 24:
        await ctx.send("Invalid input.")
        return
    sendTime = time(hour, minute, 0)
    sendTime =  datetime.combine(datetime.utcnow().date(), sendTime)
    timeToSleep = (sendTime - datetime.utcnow()).total_seconds()
    if timeToSleep < 0:
        timeToSleep += 86400
    if not await confirmation(ctx, f"Are you sure you want to reschedule to {message} UTC?"):
        await ctx.send("Cancelled.")
        return
    await ctx.send("Rescheduled to " + sendTime.strftime("%H:%M") + "UTC.")
    await TIMERS[ctx.channel.id].schedule(timeToSleep, interval).start()
    
	
@tasks.loop(seconds=15)
async def called_once_a_day(channel_id): 
    channel = client.get_channel(channel_id) 
    wh = await scraper.wikihow_random()
    embed=discord.Embed(title=wh['title'],
                        description=wh['description'],
                        color=0xFF5733,
                        image=wh['image'], 
                        url=wh['url'])
                        
    embed.set_image(url=wh['image'])
    await channel.send(embed=embed)

@called_once_a_day.before_loop
async def before_coad():
    await client.wait_until_ready()

async def set_timer(ctx, delay=0, recur=24):
    # sleep for delay
    # call set timer recursively with delay=recur and recur=recur
    coro_sleep = asyncio.sleep(delay, set_timer(ctx, recur))
    task = asyncio.ensure_future(coro_sleep)
    return task

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
    client.run(os.getenv('flimble')) 
