import discord
import config
import requests
import asyncio

client = discord.Client()


async def change_status():
    await client.wait_until_ready()
    while client.is_ready():
        await client.change_presence(activity=discord.Game(name=f"!mop | {len(client.guilds)} guilds", type=1))
        await asyncio.sleep(20)


@client.event
async def on_ready():
    print('MoppenBot op account: {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower().startswith('!mop'):
        args = message.content.split(" ")
        params = {"likes": "true"}
        if len(args) > 1:
            if args[1] == "nsfw":
                params["nsfw"] = "true"
                r = requests.get("https://moppenbot.nl/api/random/", params=params)
            elif args[1] == "stats":
                params["user"] = message.author.id
                r = requests.get("https://moppenbot.nl/api/user/", params=params)
                if r.status_code == 200:
                    data = r.json()
                    if data["success"]:
                        description = f"{data['user']['jokes']} moppen en {data['user']['likes']} likes."
                        embed = discord.Embed(title="Statistieken van " + message.author.name, description=description, color=0x00ff00)
                        await message.channel.send(embed=embed)
                        return
                embed = discord.Embed(title="Error", description="Er is een error opgetreden. Ben je al wel eens ingelogd op de site?")
                await message.channel.send(embed=embed)
            else:
                params["q"] = args
                r = requests.get("https://moppenbot.nl/api/search/", params=params)
        else:
            r = requests.get("https://moppenbot.nl/api/random/", params=params)
        if r.status_code == 200:
            data = r.json()
            if data["success"]:
                embed = discord.Embed(title="Mop " + str(data["joke"]["id"]), description=data["joke"]["joke"], color=0xffff00)
                embed.set_footer(text="Van " + str(data["joke"]["author"]) + " | " + str(data["joke"]["likes"]) + " 👍")
                msg = await message.channel.send(embed=embed)
                await msg.add_reaction("👍")
                await msg.add_reaction("🏴‍☠️")
                return
        embed = discord.Embed(title="Error", description="Er is een error opgetreden. Meld dit.")
        await message.channel.send(embed=embed)


@client.event
async def on_reaction_add(reaction, user):
    if not user.bot:
        if reaction.emoji == "👍":
            params = {
                "api_key": config.API_KEY,
                "user": user.id,
                "joke": int(reaction.message.embeds[0].title.replace("Mop ", "")),
            }
            requests.get("https://moppenbot.nl/api/like/", params=params)
        if reaction.emoji == "🏴‍☠️":
            joke_id = reaction.message.embeds[0].title.replace("Mop ", "")
            params = {
                "api_key": config.API_KEY,
                "user": user.id,
                "joke": int(joke_id),
            }
            r = requests.get("https://moppenbot.nl/api/report/", params=params)
            if r.status_code == 200:
                if r.json()["success"]:
                    embed = discord.Embed(title="Report van mop " + joke_id, description=reaction.message.embeds[0].description, color=0xff0000)
                    embed.set_footer(text="Door: " + user.name)
                    channel = client.get_channel(config.REPORT_CHANNEL)
                    await channel.send(embed=embed)

client.loop.create_task(change_status())
client.run(config.TOKEN)