Check This before writing code:

import json

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix = 'your_prefix', intents = intents)


Create a 'guilds.json' file in current directory and simply add {}

Then write the following code:
@client.event
async def on_member_join(member):
    with open('guilds.json', 'r', encoding='utf-8') as f:
        guilds_dict = json.load(f)

    channel_id = guilds_dict[str(member.guild.id)]
    await client.get_channel(int(channel_id)).send(f'{member.mention} welcome to the Otay! Support server! Enjoy your stay!')


@client.command(name='welcome')
async def set_welcome_channel(ctx, channel: discord.TextChannel):
    with open('guilds.json', 'r', encoding='utf-8') as f:
        guilds_dict = json.load(f)

    guilds_dict[str(ctx.guild.id)] = str(channel.id)
    with open('guilds.json', 'w', encoding='utf-8') as f:
        json.dump(guilds_dict, f, indent=4, ensure_ascii=False)
    
    await ctx.send(f'Sent welcome channel for {ctx.message.guild.name} to {channel.name}')