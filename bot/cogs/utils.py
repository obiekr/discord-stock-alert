import discord
import datetime as dt
from discord.ext import commands
from discord.utils import get
import asyncio
import os

from tvDatafeed import TvDatafeed, Interval
import pandas as pd
import pandas_ta as ta

class Utils(commands.Cog):
    """Utilities"""
    def __init__(self, bot):
        self.bot=bot

        self.isSending = False
        self.tickers = []

    @commands.command(name="ping")
    async def ping(self, ctx):
        """ping pong"""
        latency = round(self.bot.latency*1000)
        await ctx.send(f"Pong!\nStockBot's latency: `{str(latency)}ms`\n{os.environ['CHANNEL_ID']} {os.environ['USER_MENTION']}")

    @commands.command(name="clr")
    async def pure(self, ctx, limit:int):
        """Clear message"""
        channel = get(ctx.guild.channels, id=os.environ['CHANNEL_ID'])
        await channel.purge(limit=limit)
    
    @commands.command(name="toggle")
    async def alert(self, ctx):
        """Enable the alert"""
        if self.tickers:
            self.isSending = not self.isSending
            await ctx.send("alert is on: " + str(self.isSending))
            while self.isSending:
                hour = 2 < dt.datetime.now().hour < 8 
                if dt.datetime.now().minute % 1 == 0 and dt.datetime.now().second < 1:
                    # RUN THE SCRIPT HERE
                    # https://stackoverflow.com/questions/53486744/making-async-for-loops-in-python
                    looper = [getAndProcessHistoryData15m(ticker, ctx) for ticker in self.tickers]
                    await asyncio.gather(*looper)
                else: await asyncio.sleep(1)
        else:
            await ctx.send("Please set watchlist first")

    @commands.command(name="a")
    async def add(self, ctx, msg):
        """set ticker watchlist"""
        msg = msg.strip().upper()
        try:
            self.tickers.append(msg)
            await ctx.send(f"{msg} added to watchlist")
        except:
            await ctx.send(f"{msg} failed adding to watchlist")
    
    @commands.command(name="r")
    async def rem(self, ctx, msg):
        """delete ticker from watchlist"""
        msg = msg.strip().upper()
        try:
            self.tickers.remove(msg)
            await ctx.send(f"{msg} removed from watchlist")            
        except:
            await ctx.send(f"{msg} doesn't exist in watchlist")

    @commands.command(name="see")
    async def see(self, ctx):
        """view the watchlist"""
        msg = "```Current watchlist: \n"
        for x in self.tickers:
            msg += x
            msg += "\n"
        msg += "```"
        await ctx.send(msg)


def setup(bot):
    bot.add_cog(Utils(bot))

async def getAndProcessHistoryData15m(ticker, ctx):
    tv = TvDatafeed()
    df = tv.get_hist(ticker, "IDX", interval=Interval.in_30_minute, n_bars= 1460)
    df.reset_index(inplace=True)
    df1 = df
    lenfast = 30
    lenslow = 1100
    
    df1["close_change"] = df1["close"].diff()
    df1["close_change"].loc[df1["close_change"] < 0] = 0
    df1["up_slow"] = ta.rma(df1["close_change"], length=lenslow)
    df1["up_fast"] = ta.rma(df1["close_change"], length=lenfast)

    df1["close_change"] = df1["close"].diff()
    df1["close_change"].loc[df1["close_change"] > 0] = 0
    df1["close_change"].loc[df1["close_change"] < 0] = abs(df1["close_change"].loc[df1["close_change"] < 0])
    df1["down_slow"] = ta.rma(df1["close_change"], length=lenslow)
    df1["down_fast"] = ta.rma(df1["close_change"], length=lenfast)

    df1["rsi_fast"] = df1["down_fast"]
    df1["rsi_fast"].loc[df1["down_fast"] == 0] = 100
    df1["rsi_fast"].loc[df1["up_fast"] == 0] = 0
    df1["rsi_fast"].loc[df1["up_fast"] != 0] = 100 - (100 / (1 + (df1["up_fast"] / df1["down_fast"])))

    df1["rsi_slow"] = df1["down_slow"]
    df1["rsi_slow"].loc[df1["down_slow"] == 0] = 100
    df1["rsi_slow"].loc[df1["up_slow"] == 0] = 0
    df1["rsi_slow"].loc[df1["up_slow"] != 0] = 100 - (100 / (1 + (df1["up_slow"] / df1["down_slow"])))

    df1["divergence"] = df1["rsi_fast"] - df1["rsi_slow"]
    
    df1.ta.sma(length=30, append=True)
    df1.ta.sma(length=100, append=True)

    buy_con1 = df1["SMA_30"].iloc[-1] >= df1["SMA_30"].iloc[-1] and df1["divergence"] > 0
    buy_con2 = df1["close"].iloc[-1] < df1["open"].iloc[-1] and df1["close"].iloc[-1] < df1["SMA_30"].iloc[-1]

    sell_con1 = df1["close"].iloc[-1] < df1["SMA_30"].iloc[-1] and df1["divergence"].iloc[-1] < 0
    sell_con2 = df1["close"].iloc[-1] < df1["SMA_100"].iloc[-1]

    if buy_con1 and buy_con2:
        ctx.send(f"{ticker} Buy " + os.environ['USER_MENTION'])
    if sell_con1 or sell_con2:
        ctx.send(f"{ticker} Sell "+ os.environ['USER_MENTION'])

    

