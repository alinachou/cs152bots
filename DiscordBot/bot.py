# bot.py
import discord
from discord.ext import commands
import os
import json
import logging
import re
import requests
from report import Report
import pdb
import asyncio

# Set up logging to the console
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# There should be a file called 'tokens.json' inside the same folder as this file
token_path = 'tokens.json'
if not os.path.isfile(token_path):
    raise Exception(f"{token_path} not found!")
with open(token_path) as f:
    # If you get an error here, it means your token is formatted incorrectly. Did you put it in quotes?
    tokens = json.load(f)
    discord_token = tokens['discord']
    openai_token = tokens['openai_key']
    openai_org = tokens['openai_org']
    perspective_token = tokens['perspective']


class ModBot(discord.Client):
    def __init__(self): 
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='.', intents=intents)
        self.group_num = None
        self.mod_channels = {} # Map from guild to the mod channel id for that guild
        self.reports = {} # Map from user IDs to the state of their report
        self.channel_id = 1103033289503166540
        self.mod_id = 1103033289503166541

    async def on_ready(self):
        print(f'{self.user.name} has connected to Discord! It is these guilds:')
        for guild in self.guilds:
            print(f' - {guild.name}')
        print('Press Ctrl-C to quit.')

        # Parse the group number out of the bot's name
        match = re.search('[gG]roup (\d+) [bB]ot', self.user.name)
        if match:
            self.group_num = match.group(1)
        else:
            raise Exception("Group number not found in bot's name. Name format should be \"Group # Bot\".")

        # Find the mod channel in each guild that this bot should report to
        for guild in self.guilds:
            for channel in guild.text_channels:
                if channel.name == f'group-{self.group_num}-mod':
                    self.mod_channels[guild.id] = channel
        

    async def on_message(self, message):
        '''
        This function is called whenever a message is sent in a channel that the bot can see (including DMs). 
        Currently the bot is configured to only handle messages that are sent over DMs or in your group's "group-#" channel. 
        '''
        # Ignore messages from the bot 
        if message.author.id == self.user.id:
            return

        # Check if this message was sent in a server ("guild") or if it's a DM
        if message.guild:
            await self.handle_channel_message(message)
        else:
            await self.handle_dm(message)

    async def handle_dm(self, message):
        # Handle a help message
        if message.content == Report.HELP_KEYWORD:
            reply =  "Use the `report` command to begin the reporting process.\n"
            reply += "Use the `cancel` command to cancel the report process.\n"
            await message.channel.send(reply)
            return

        author_id = message.author.id
        responses = []

        # Only respond to messages if they're part of a reporting flow
        if author_id not in self.reports and not message.content.startswith(Report.START_KEYWORD):
            return

        # If we don't currently have an active report for this user, add one
        if author_id not in self.reports:
            self.reports[author_id] = Report(self)

        # Let the report class handle this message; forward all the messages it returns to uss
        responses = await self.reports[author_id].handle_message(message)
        for r in responses:
            await message.channel.send(r)

        # If the report is complete or cancelled, remove it from our map
        if self.reports[author_id].report_complete():
            print("report complete")
            reply = "This report is complete."
            for guild in self.guilds:
                for channel in guild.text_channels:
                    if channel.name == f'group-{self.group_num}-mod':
                        self.mod_channels[guild.id] = channel
                        report_info = self.reports[author_id]
                        report_details = "**Report Details**\n\n"
                        report_details += f"**User:** {message.author.name}\n"
                        report_details += f"**Report Category:** {report_info.report_category}\n"
                        report_details += f"**Message Content that the User Wish to Report:** ``{report_info.report_content}``\n"
                        report_details += f"**Message Link:** {report_info.message_link}\n"
                        report_details += f"**Report Description:** {report_info.report_description}\n\n"
                        await channel.send(report_details)

                        moderator_action = "Moderators please choose from the following categories to determine the result of this report.\n"
                        moderator_action += "1️⃣: Reported message does not violate Community Guidelines for the specified category.\n"
                        moderator_action += "2️⃣: Reported message does violate Community Guidelines for the specified category."
                        response_message = await channel.send(moderator_action)

                        await response_message.add_reaction('1️⃣')
                        await response_message.add_reaction('2️⃣')

                        # Define a check function for the reaction
                        def check(reaction, user):
                            return str(reaction.emoji) in ['1️⃣', '2️⃣']
                        
                        try:
                            # Wait for a reaction
                            reaction, _ = await client.wait_for("reaction_add", timeout=1000000, check=check)
                            if str(reaction.emoji) == '1️⃣':
                                await channel.send("Moderation Team informs the reporter that the reported message did not violate any Community Guidelines.")
                                await message.channel.send("After looking through the report, the moderation team has decided that the reported message did not violate any Community Guidelines.")
                            elif str(reaction.emoji) == '2️⃣':
                                await channel.send("Moderation Team removes the reported message.")
                                await message.channel.send("After looking through the report, the moderation team has decided that the reported message did violate the Community Guidelines.")

                        except asyncio.TimeoutError:
                            await channel.send('You did not react in time.')
            
            self.reports.pop(author_id)
            return [reply]

    async def handle_channel_message(self, message):
        # Only handle messages sent in the "group-#" channel
        if not message.channel.name == f'group-{self.group_num}':
            return

        # Forward the message to the mod channel
        mod_channel = self.mod_channels[message.guild.id]
        await mod_channel.send(f'Forwarded message:\n{message.author.name}: "{message.content}"')
        scores = self.eval_text(message.content)
        await mod_channel.send(self.code_format(scores))

    
    def eval_text(self, message):
        ''''
        TODO: Once you know how you want to evaluate messages in your channel, 
        insert your code here! This will primarily be used in Milestone 3. 
        '''
        # api calls here:

        response = 0 # add in what we want to differentiate to this varaible
        tup = (message, response)
        return tup

    
    def code_format(self, text):
        ''''
        TODO: Once you know how you want to show that a message has been 
        evaluated, insert your code here for formatting the string to be 
        shown in the mod channel. 
        '''

        message, response = text
        if response == 1:
            return "This message was automatically flagged: '" + message+"'"
            # maybe we even add this data to a backend, SQL database maybe?
        return "Evaluated: '" + message + "'"


client = ModBot()
client.run(discord_token)