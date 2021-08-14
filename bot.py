import asyncio
import logging
import discord
from discord.ext.commands import Bot
from discord.ext.commands.errors import MissingRequiredArgument
import os
from dotenv import load_dotenv
import collector
import json
import f5interface

logging.basicConfig(level=logging.INFO)
load_dotenv()

try:
    with open('keywords.txt') as f:
        keywords = f.readlines()
except:
    keywords = []

try:
    with open('anchors.json') as f:
        anchors = json.load(f)
except:
    anchors = {'':[]}
    anchors.update({k:[] for k in keywords})


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

@client.command(name='keywords')
async def print_kwords(ctx):
    await ctx.send('```'+'\n'.join(k for k in keywords)+'```')

@client.command(name='anchor', description='send f5bot messages here')
async def anchor(ctx, keyword=''): # for lack of a better adjective
    channel = ctx.channel.id
    print(repr(keyword))
    if keyword == '':
        if channel in anchors['']:
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
            return      
    if keyword not in keywords:
        await ctx.send('Keyword has not been added yet.')
        return
    if channel in anchors[keyword]:
        await ctx.send('Channel already receiving alerts for this keyword.')
    else:
        anchors[keyword].append(channel)
        await ctx.send('Channel now receiving alerts for this keyword.')

@client.command(name='check', description='check inbox', help='check inbox')
async def check_mail(ctx):
    logging.info(ctx.author.__str__()+' requested a inbox check')
    res = collector.check_inbox()
    if len(res) == 0:
        embed=discord.Embed(title="sorry bruh",
                        description="theres nothing",
                        color=0xFF5733)
        await ctx.send(embed=embed)
        return
    for i in res:
        parsed = collector.parse(i)
        for keyword, head, link, location in parsed:
            embed=discord.Embed(title=head,
                                url=link,
                                description=location,
                                color=0x0096FF)

            await send_alert(keyword, ctx, embed=embed)

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

@client.event
async def on_ready():
    logging.info("Ready")
    await check_mail_automatic()
    
client.run(os.getenv('flimble'))
with open('anchors.json','w') as f:
    json.dump(anchors, f, indent=4)
with open('keywords.txt','w') as f:
    f.write('\n'.join(keywords))
