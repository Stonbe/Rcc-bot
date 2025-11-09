import os
import discord
from discord.ext import commands
from discord import app_commands, ui, ButtonStyle
from urllib.parse import urlparse

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 1434590759570378774  # replace with your server ID
GUILD = discord.Object(id=GUILD_ID)

IMAGE_URL = "https://i.ytimg.com/vi/vIDAXZ2HT38/hq720.jpg?sqp=-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD&rs=AOn4CLCqSI_HuzVFSS0EpodH2a_U0s7Tqwwhol"
ROLE_ID = 1434592997869228052  # replace with the ID of the role allowed to run the command

class SessionView(ui.View):
    def __init__(self, max_reactions: int, link: str):
        super().__init__(timeout=180)
        self.max_reactions = max_reactions
        self.link = link
        self.current_reactions = 0
        self.reacted_users = set()

        self.react_button = ui.Button(label="React (0/0)", style=ButtonStyle.primary)
        self.react_button.callback = self.react_callback
        self.add_item(self.react_button)

    async def react_callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        if user_id in self.reacted_users:
            self.reacted_users.remove(user_id)
            self.current_reactions -= 1
        else:
            self.reacted_users.add(user_id)
            self.current_reactions += 1

        self.react_button.label = f"React ({self.current_reactions}/{self.max_reactions})"
        await interaction.response.edit_message(view=self)

        if self.current_reactions >= self.max_reactions:
            self.remove_item(self.react_button)
            join_button = ui.Button(label="Join", style=ButtonStyle.success)
            join_button.callback = self.join_callback
            self.add_item(join_button)
            await interaction.message.edit(view=self)

    async def join_callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Here’s the session link: {self.link}", ephemeral=True)

def has_role(interaction: discord.Interaction):
    role = discord.utils.get(interaction.user.roles, id=ROLE_ID)
    return role is not None

@bot.tree.command(name="start", description="Create a session embed", guild=GUILD)
@app_commands.check(has_role)
@app_commands.describe(
    channel="Channel to send the embed in",
    ping="Ping type (@here, @everyone, none)",
    location="Session location",
    theme="Session theme",
    reactions="Number of reactions needed",
    link="Session link"
)
async def session(interaction: discord.Interaction, channel: discord.TextChannel, ping: str, location: str, theme: str, reactions: int, link: str):
    ping_text = ""
    if ping.lower() == "@here":
        ping_text = "@here"
    elif ping.lower() == "@everyone":
        ping_text = "@everyone"

    if ping_text:
        await channel.send(ping_text)

    parsed_url = urlparse(link)
    title = parsed_url.netloc.replace("www.", "").capitalize() or "Session"

    embed = discord.Embed(title=title, color=discord.Color.blue())
    embed.add_field(name="Host", value=interaction.user.mention, inline=False)
    embed.add_field(name="Location", value=location, inline=True)
    embed.add_field(name="Theme", value=theme, inline=True)
    embed.set_image(url=IMAGE_URL)

    view = SessionView(max_reactions=reactions, link=link)
    await channel.send(embed=embed, view=view)
    await interaction.response.send_message(f"Session sent in {channel.mention}", ephemeral=True)

@session.error
async def session_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message("You do not have permission to run this command.", ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync(guild=GUILD)
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('Slash commands synced!')

bot.run(os.environ['BOT_TOKEN'])
