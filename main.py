import discord
from discord.ext import commands, tasks
import random
import asyncio

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

# Global variable to store the channel ID where monsters will spawn
spawn_channel_id = None

# Dictionary to store monsters and their details
monsters = [
    {
        'name': 'Ghazt',
        'image': 'https://media.discordapp.net/attachments/1354151223409901700/1354151962589003786/Untitled421_20250220170540.png',
        'emoji': '<:Ghazt:1354497826985480213>'
    },
    {
        'name': 'Grumpyre',
        'image': 'https://media.discordapp.net/attachments/1354151223409901700/1354151963171885227/Untitled422_20250223155434.png',
        'emoji': '<:Grumpyre:1354498036012810365>'
    }
]

# Dictionary to store user's collected monsters
user_collections = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    spawn_monster.start()

@bot.command()
@commands.has_permissions(administrator=True)
async def config_channel(ctx, channel_id: int):
    global spawn_channel_id
    spawn_channel_id = channel_id
    await ctx.send(f'Spawn channel set to <#{channel_id}>')

@bot.command()
async def claim(ctx):
    await ctx.send(f'{ctx.author.mention}, you claimed a random monster!')

@bot.command()
async def monster_completion(ctx):
    embed = discord.Embed(title="Monster Completion")
    embed.description = "Here are the monsters you've collected and those you haven't."
    # Add more embed details based on your completion logic
    await ctx.send(embed=embed)

@tasks.loop(minutes=random.randint(15, 20))
async def spawn_monster():
    if spawn_channel_id:
        channel = bot.get_channel(spawn_channel_id)
        if channel:
            monster = random.choice(monsters)
            message = await channel.send(
                f"A Wild Bonk Appeared!\n{monster['image']}",
                components=[
                    discord.ui.Button(label='Catch', custom_id='catch_button')
                ]
            )
            try:
                interaction = await bot.wait_for(
                    'interaction',
                    check=lambda i: i.custom_id == 'catch_button' and i.message.id == message.id,
                    timeout=60.0
                )
                await interaction.response.send_modal(
                    title='Catch the Monster',
                    custom_id='catch_modal',
                    components=[
                        discord.ui.TextInput(label='Monster Name', custom_id='monster_name')
                    ]
                )
                modal_interaction = await bot.wait_for(
                    'modal_submit',
                    check=lambda i: i.custom_id == 'catch_modal' and i.message.id == message.id,
                    timeout=60.0
                )
                if modal_interaction.data['components'][0]['value'] == monster['name']:
                    await message.edit(content=f"{interaction.user.mention} caught the monster!", components=[])
                else:
                    await interaction.response.send_message("You typed it wrong! Try again.")
            except asyncio.TimeoutError:
                await message.delete()

bot.run('YOUR_BOT_TOKEN')
