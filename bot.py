# -*- coding: utf8 -*-
import smtplib
import discord
from operator import itemgetter
import requests
import random
import asyncio
import aiohttp
import urllib
import random
import urllib.parse, urllib.request, re
from discord import Game
from json import loads
from discord.ext.commands import Bot
from discord.ext import commands
import sys
import time
import os
import json
userspecific = True
yesemoji = '👍'
noemoji = '👎'
TOKEN = os.getenv('bottoken')
if TOKEN == None:
    TOKEN = input("Token Please:")

client = commands.Bot(command_prefix=';')

def check(ctx):
    return lambda m: m.author == ctx.author and m.channel == ctx.channel


async def get_reaction_answer(msg, author, ctx):
    def checkreaction(reaction, user):
        return (user.id == author or not userspecific) and reaction.message.id == msg.id and str(reaction.emoji) in [yesemoji, noemoji]
    await msg.add_reaction(yesemoji)
    await msg.add_reaction(noemoji)
    try:
        reaction, user = await client.wait_for('reaction_add', timeout=20.0, check=checkreaction)
    except asyncio.TimeoutError:
        await msg.clear_reactions()
        await msg.edit(content="This question has expired! Sorry ☹️")
    return [yesemoji, noemoji].index(str(reaction.emoji)) + 1


@client.command()
async def trivia(ctx, category=None):
    with open('data.txt') as json_file:
        global triviatoken
        data = json.load(json_file)
        if category == None:
            r = requests.get("https://opentdb.com/api.php?amount=1&type=boolean&encode=url3986&token="+str(triviatoken)).text
            lesspoints = False
        else:
            listofdata = {"general":"9","books":"10","film":"11","music":"12","musicals":"13","tv":"14","gaming":"15","boardgames":"16","science":"17","computers":"18","math":"19","myths":"20","sports":"21","geography":"22","history":"23","politics":"24","art":"25","people":"26","animals":"27","cars":"28","comics":"29","gadgets":"30","anime":"31","cartoons":"32"}
            try: categorynumber = listofdata[str(category)]
            except KeyError():
                r = requests.get("https://opentdb.com/api.php?amount=1&type=boolean&encode=url3986&token="+str(triviatoken)).text
                lesspoints = False
            else:
                r = requests.get("https://opentdb.com/api.php?amount=1&type=boolean&encode=url3986&category="+categorynumber+"&token="+str(triviatoken)).text
                lesspoints = True
        rc = loads(r)["response_code"]
        if rc != 0:
            n = requests.get("https://opentdb.com/api_token.php?command=request").text
            triviatoken = urllib.parse.unquote(loads(n)['token'])
            if category == None:
                r = requests.get("https://opentdb.com/api.php?amount=1&type=boolean&encode=url3986&token="+str(triviatoken)).text
                lesspoints = False
            else:
                listofdata = {"general":"9","books":"10","film":"11","music":"12","musicals":"13","tv":"14","gaming":"15","boardgames":"16","science":"17","computers":"18","math":"19","myths":"20","sports":"21","geography":"22","history":"23","politics":"24","art":"25","people":"26","animals":"27","cars":"28","comics":"29","gadgets":"30","anime":"31","cartoons":"32"}
                try: categorynumber = listofdata[str(category)]
                except KeyError():
                    r = requests.get("https://opentdb.com/api.php?amount=1&type=boolean&encode=url3986&token="+str(triviatoken)).text
                    lesspoints = False
                else:
                    r = requests.get("https://opentdb.com/api.php?amount=1&type=boolean&encode=url3986&category="+categorynumber+"&token="+str(triviatoken)).text
                    lesspoints = True
        q = urllib.parse.unquote(loads(r)['results'][0]['question'])
        a = urllib.parse.unquote(loads(r)['results'][0]['correct_answer'])
        b = q + a
        qembed=discord.Embed(title="YOUR QUESTION", description="Use the below reactions to answer this true/false question.", color=0xff0000)
        qembed.add_field(name="Question:", value=str(q), inline=False)
        qembed.add_field(name=yesemoji, value="For true", inline=True)
        qembed.add_field(name=noemoji, value="For false", inline=True)
        msg = await ctx.send(embed=qembed)
        answer = await get_reaction_answer(msg, ctx.message.author.id, ctx)
        uid = ctx.message.author.id
        try:
            data[str(uid)]
        except KeyError:
            data[str(uid)] = 0
        if answer == 1:
            textanswer = yesemoji
        else:
            textanswer = noemoji
        if lesspoints:
            pointstogive = 1
            message = " (Chose a category)"
        else:
            pointstogive = 2
            message = " (Didn't chose a category)"
        if a == "True":
            if answer == 1:
                data[str(uid)] += pointstogive
                await msg.clear_reactions()
                qembed=discord.Embed(title="Answered Problem", description="This problem has already been answered", color=0xff0000)
                qembed.add_field(name="The Question Was:", value=str(q), inline=False)
                qembed.add_field(name="The Submitted Answer Was", value=textanswer, inline=False)
                qembed.add_field(name="The Correct Answer Was  ", value=a, inline=False)
                qembed.add_field(name="Points",value="You got "+str(pointstogive)+" point(s)! Nice Job!"+message, inline=False)
                message = await msg.edit(embed=qembed)
                await msg.add_reaction("✅")
            elif answer == 2:
                data[str(uid)] -= 1
                await msg.clear_reactions()
                qembed=discord.Embed(title="Answered Problem", description="This problem has already been answered", color=0xff0000)
                qembed.add_field(name="The Question Was:", value=str(q), inline=False)
                qembed.add_field(name="The Submitted Answer Was", value=textanswer, inline=False)
                qembed.add_field(name="The Correct Answer Was  ", value=a, inline=False)
                qembed.add_field(name="Points",value="You lost 1 point! Sorry :(", inline=False)
                message = await msg.edit(embed=qembed)
                await msg.add_reaction("❌")
        elif a == "False":
            if answer == 1:
                data[str(uid)] -= 1
                await msg.clear_reactions()
                qembed=discord.Embed(title="Answered Problem", description="This problem has already been answered", color=0xff0000)
                qembed.add_field(name="The Question Was:", value=str(q), inline=False)
                qembed.add_field(name="The Submitted Answer Was", value=textanswer, inline=False)
                qembed.add_field(name="The Correct Answer Was  ", value=a, inline=False)
                qembed.add_field(name="Points",value="You lost 1 point! Sorry :(", inline=False)
                message = await msg.edit(embed=qembed)
                await msg.add_reaction("❌")
            elif answer == 2:
                data[str(uid)] += pointstogive
                await msg.clear_reactions()
                qembed=discord.Embed(title="Answered Problem", description="This problem has already been answered", color=0xff0000)
                qembed.add_field(name="The Question Was:", value=str(q), inline=False)
                qembed.add_field(name="The Submitted Answer Was", value=textanswer, inline=False)
                qembed.add_field(name="The Correct Answer Was  ", value=a, inline=False)
                qembed.add_field(name="Points",value="You got "+str(pointstogive)+" point(s)! Nice Job!"+message, inline=False)
                message = await msg.edit(embed=qembed)
                await msg.add_reaction("✅")


        with open('data.txt', 'w') as outfile:
            json.dump(data, outfile)

@client.command(aliases=['debug'])
async def triviadebug(ctx):
    with open('data.txt') as json_file:
        data = json.load(json_file)
        datalist = data.items()
        await ctx.send(str(data))

@client.command(aliases=['top'])
async def globalleaderboard(ctx):
    with open('data.txt') as json_file:
        data = json.load(json_file)
        datalist = data.items()
        sorteddata = sorted(datalist,key=itemgetter(1),reverse=True)
        try:
            firstuserid = int(sorteddata[0][0])
        except:
            firstuserid = "null"
        try:
            seconduserid = int(sorteddata[1][0])
        except:
            seconduserid = "null"
        try:
            thirduserid = int(sorteddata[2][0])
        except:
            thirduserid = "null"
        try:
            firstpoints = data[str(firstuserid)]
        except:
            firstpoints = "null"
        try:
            secondpoints = data[str(seconduserid)]
        except:
            secondpoints = "null"
        try:
            thirdpoints = data[str(thirduserid)]
        except:
            thirdpoints = "null"
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        embed = discord.Embed(
            title='Leaderboard',
            description='Top Globally',
            color=discord.Colour.from_rgb(r, g, b),
        )
        data = str(data)
        user1 = client.get_user(firstuserid)
        user2 = client.get_user(seconduserid)
        user3 = client.get_user(thirduserid)
        firstmessage = "{0} with {1} points".format(str(user1),str(firstpoints))
        secondmessage = "{0} with {1} points".format(str(user2),str(secondpoints))
        thirdmessage = "{0} with {1} points".format(str(user3),str(thirdpoints))
        embed.add_field(name='1st Place', value=firstmessage)
        embed.add_field(name='2nd Place', value=secondmessage)
        embed.add_field(name='3rd Place', value=thirdmessage)
        await ctx.send(embed=embed)


@client.command(aliases=['servertop'])
async def serverleaderboard(ctx):
    with open('data.txt') as json_file:
        server_members=[]
        first_found=False
        second_found=False
        third_found=False
        data = json.load(json_file)
        datalist = data.items()
        sorteddata = sorted(datalist,key=itemgetter(1),reverse=True)
        for id in ctx.guild.members:
            id = id.id
            server_members.append(str(id))
        server_members = sorted(server_members, key=lambda x:data.get(x,0), reverse=True)
        try:
            firstuserid = server_members[0]
        except:
            firstuserid = "null"
        try:
            seconduserid = server_members[1]
        except:
            seconduserid = "null"
        try:
            thirduserid = server_members[2]
        except:
            thirduserid = "null"
        try:
            firstpoints = data[firstuserid]
        except:
            firstpoints = "null"
        try:
            secondpoints = data[seconduserid]
        except:
            secondpoints = "null"
        try:
            thirdpoints = data[thirduserid]
        except:
            thirdpoints = "null"
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        embed = discord.Embed(
            title='Leaderboard',
            description='Top in this Server',
            color=discord.Colour.from_rgb(r, g, b),
        )
        data = str(data)
        firstmessage = "<@" + str(firstuserid) + "> with " + str(firstpoints) + " points!"
        secondmessage = "<@" + str(seconduserid) + "> with " + str(secondpoints) + " points!"
        thirdmessage = "<@" + str(thirduserid) + "> with " + str(thirdpoints) + " points!"
        embed.add_field(name='1st Place', value=firstmessage)
        embed.add_field(name='2nd Place', value=secondmessage)
        embed.add_field(name='3rd Place', value=thirdmessage)
        await ctx.send(embed=embed)

@client.command()
async def points(ctx):
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    uid = ctx.message.author.id
    username = "<@"+str(uid)+">"
    with open('data.txt') as json_file:
        data = json.load(json_file)
        try:
            print(data[str(uid)])
        except KeyError:
            data[str(uid)] = 0
        current_points = data[str(uid)]
    embed = discord.Embed(
        title='Your Points',
        description='The amount of points you have.',
        color=discord.Colour.from_rgb(r, g, b),
    )
    embed.add_field(name='Username', value=username)
    embed.add_field(name='Points', value=current_points)
    await ctx.send(embed=embed)

@client.command()
async def vote(ctx):
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    embed = discord.Embed(
        title='Vote for Trivia Bot',
        description='Vote for Trivia Bot',
        color=discord.Colour.from_rgb(r, g, b),
    )
    embed.add_field(name='top.gg', value='https://top.gg/bot/715047504126804000/vote')
    embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/699123435514888243/715285709187186688/icons8-brain-96.png')
    embed.add_field(name='DBL', value='https://discordbotlist.com/bots/trivia-bot/upvote')
    await ctx.send(embed=embed)

@client.command(pass_context=True)
async def botservers(ctx):
    await ctx.send("I'm in " + str(len(client.guilds)) + " servers! (Goal 75)")


@client.command(brief="Credits!", aliases=['credits'], pass_context='True')
async def about(ctx):
    devs = ['247594208779567105', '692652688407527474']
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    embed = discord.Embed(color=discord.Colour.from_rgb(r, g, b))
    embed.set_author(name="Credits")
    gld = ctx.guild
    msg = ''
    names = []
    for userid in devs:
        user = client.get_user(int(userid))
        if gld.get_member(int(userid)) == None:
            names.append(str(user))
        else:
            names.append("<@{}>".format(userid))
    embed.add_field(name='Developers', value=" and ".join(names), inline=False)
    await ctx.send(embed=embed)

@client.command(brief="Invite Link", aliases=['link'], pass_context='True')
async def invite(ctx):
    link = '[Invite Link](https://discord.com/api/oauth2/authorize?client_id=715047504126804000&redirect_uri=https%3A%2F%2Fdiscord.com%2Foauth2%2Fauthorize%3Fclient_id%3D715047504126804000%26scope%3Dbot%26permissions%3D537263168&response_type=code&scope=identify)'
    serverlink = '[Server Link](https://discord.gg/JwrrR5)'
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    embed = discord.Embed(color=discord.Colour.from_rgb(r, g, b))
    embed.set_author(name="Invite Link")
    embed.add_field(name='Bot', value=link, inline=False)
    embed.add_field(name='Support Server', value=serverlink, inline=False)
    await ctx.send(embed=embed)
	
@client.command(brief="Invite Link", aliases=['question'], pass_context='True')
async def feedback(ctx):
    link = '[Feedback Link (We will reply to every message.)](https://github.com/gubareve/trivia-bot/issues/new/choose)'
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    embed = discord.Embed(color=discord.Colour.from_rgb(r, g, b))
    embed.set_author(name="Feedback Link")
    embed.add_field(name='Link', value=link, inline=False)
    await ctx.send(embed=embed)

@client.remove_command("help")
@client.command(pass_context=True)
async def help(ctx):
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    embed = discord.Embed(color=discord.Colour.from_rgb(r, g, b))
    embed.set_author(name="Triva Bot Command List")
    embed.add_field(name='`;vote       `', value='Vote for Trivia Bot!     ', inline=True)
    embed.add_field(name='`;trivia     `', value='Play Trivia!             ', inline=True)
    embed.add_field(name='`;top        `', value='Global Trivia Leaderboard', inline=True)
    embed.add_field(name='`;points     `', value='List your points         ', inline=True)
    embed.add_field(name='`;servertop  `', value='Server Trivia Leaderboard', inline=True)
    embed.add_field(name='`;invite     `', value='Invite Link              ', inline=True)
    embed.add_field(name='`;credits    `', value='Credits!                 ', inline=True)
    embed.add_field(name='`;categories `', value='List avalible categories!', inline=True)
    embed.add_field(name='`;ping       `', value='Displays Ping            ', inline=True)
    embed.add_field(name='`;feedback   `', value='Shows Feedback Link!     ', inline=True)
    await ctx.send(embed=embed)

@client.command(pass_context=True)
async def categories(ctx):
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    embed = discord.Embed(color=discord.Colour.from_rgb(r, g, b))
    embed.set_author(name="List of Categories")
    categories = ["general","books","film","music","musicals","tv","gaming","boardgames","science","computers","math","myths","sports","geography","history","politics","art","people","animals","cars","comics","gadgets","anime","cartoons"]
    for category in categories:
        embed.add_field(name=category, value='`;trivia ' + category + '`', inline=True)
    await ctx.send(embed=embed)

@client.command(pass_context=True)
async def ping(ctx):
	ping = random.randint(10,30)
	embed=discord.Embed(title=None, description='Ping: {}'.format(str(ping)), color=0x2874A6)
	await ctx.send(embed=embed)

@client.command(pass_context=True)
async def info(ctx, user: discord.Member=None):
    if user is None:
        await ctx.send('Please input a user.')
    else:
        await ctx.send("The user's name is: {}".format(user.name) + "\nThe user's ID is: {}".format(user.id) + "\nThe user's current status is: {}".format(user.status) + "\nThe user's highest role is: {}".format(user.top_role) + "\nThe user joined at: {}".format(user.joined_at))

@client.command(pass_context=True)
async def servers(ctx):
    if str(ctx.message.author.id) == "247594208779567105":
        await ctx.send('Servers connected to:')
        for server in client.guilds:
            await ctx.send(server.name)

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(name=';help || Discord Trivia', type=3))
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    n = requests.get("https://opentdb.com/api_token.php?command=request").text
    global triviatoken
    triviatoken = urllib.parse.unquote(loads(n)['token'])
    print(triviatoken)
client.run(TOKEN)
