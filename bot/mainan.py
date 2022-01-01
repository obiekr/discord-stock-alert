import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

class Bot(commands.Bot):
    def __init__(self):
        self.__cogs = [
            "bot.cogs.utils"
        ]
        super().__init__(command_prefix=self.prefix, case_insensitive=True, intents=discord.Intents.all())

    def setup(self):
        print("Setting up...")
        for ext in self.__cogs:
            self.load_extension(ext)
            print(f"# Loaded {ext}")
        #tempat code-code awal

    def run(self):
        self.setup()
        load_dotenv() 
        token = os.getenv("TOKEN")
        print("Running bot...")
        super().run(token, bot=True, reconnect=True)

    async def prefix(self, bot, msg):
        return commands.when_mentioned_or("-")(bot, msg)

    async def on_ready(self):
        print("Bot is ready")















