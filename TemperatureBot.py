from datetime import datetime
import asyncio
from aiohttp.client import post
import discord
from discord.utils import get

# create client
client = discord.Client()

def read(i):
    location = '/sys/bus/w1/devices/'+i+'/w1_slave'
    tfile = open(location)
    text = tfile.read()
    tfile.close()
    secondline = text.split("\n")[1]
    temperaturedata = secondline.split(" ")[9]
    temperature = float(temperaturedata[2:])
    celcius = temperature / 1000
    farenheit = (celcius * 1.8) + 32
    rounded_farenheit = round(farenheit,1)
    return_str = str(rounded_farenheit) + " °F"
    return return_str


# Create Message Function
async def mainloop():
    global done

    post_time = 57

    now = datetime.now()
    minute = now.minute

    if enabled == True and done == False and minute == post_time:
        #message = read(TempProbe)
        message = 'test'
        await client.send_message(client.get_channel('874098096680886292'), message)
        done = True
    elif minute != post_time:
        done = False

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
            await asyncio.sleep(1)

@client.event
async def on_message(message):

  if str(message.channel) == "temperature":

    if str(message.author) != "TemperatureBot#0960":

        if message.content == "clear" or message.content == "Clear":

            message.channel.fetchMessages()

            await client.delete_message(message)
            print('clearing')
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