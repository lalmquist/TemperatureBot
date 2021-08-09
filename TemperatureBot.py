from datetime import datetime
import asyncio
from aiohttp.client import post
import discord
from discord.utils import get

# create client
client = discord.Client()

# read temperature from temperature probe on raspberry pi
# returns fahrenheit
def read(i):
    location = '/sys/bus/w1/devices/'+ i +'/w1_slave'
    tfile = open(location)
    text = tfile.read()
    tfile.close()
    secondline = text.split("\n")[1]
    temperaturedata = secondline.split(" ")[9]
    temperature = float(temperaturedata[2:])
    
    # Celcius
    celcius = temperature / 1000

    # Fahrenheit
    fahrenheit = (celcius * 1.8) + 32
    rounded_fahrenheit = round(fahrenheit,1)
    return_str = str(rounded_fahrenheit) + " °F"
    
    return return_str


# Create Message Function
async def mainloop():
    global done

    # auto post temperature every hour (at minute 0)
    post_time = 0

    now = datetime.now()
    minute = now.minute

    # wait for bot to be ready and not already posted this hour
    if enabled == True and done == False and minute == post_time:
        message = read(TempProbe)
        # post temperature in channel
        await client.send_message(client.get_channel('874098096680886292'), message)
        done = True
    elif minute != post_time:
        done = False

# looping Cog
class MyCog(object):
    def __init__(self,bot):
        self.bot = bot
        self.looped_task = bot.create_task(self.looping_function())
        self.data = {}
    
    def __unload(self):
        try:
            self.looped_task.cancel()
        except (AttributeError, asyncio.CancelledError):
            pass
    
    async def do_stuff(self):
        await mainloop()

    async def looping_function(self):
        while True:
            await self.do_stuff()
            # pause X seconds between main loops
            await asyncio.sleep(1)

@client.event
async def on_message(message):
# if somebody posts in temp channel
  if str(message.channel) == "temperature":
    if str(message.author) != "TemperatureBot#0960":
        
        # delete channel messages
        if message.content.lower() == "clear":
            message.channel.fetchMessages()
            await client.delete_message(message)
            print('clearing')
            
        # delete their message, then post temperature
        else:
            await client.delete_message(message)
            message = read(TempProbe)
            await client.send_message(client.get_channel('874098096680886292'), message)

@client.event
async def on_ready():
    global enabled
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    enabled = True            

if __name__ == "__main__":
    # init globals
    TempProbe = "28-051760d567ff"
    enabled = False
    done = False
    
    loop = asyncio.get_event_loop()
    Daily_Poster = MyCog
    Daily_Poster(loop)

    # read secret discord token
    f=open("token.txt","r")
    if f.mode == 'r':
        discordToken = f.read()

    client.run(discordToken)