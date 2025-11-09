import os
import discord
from discord.ext import commands
from discord import app_commands, ui, ButtonStyle
from urllib.parse import urlparse

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = Tru

bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 1434590759570378774
GUILD = discord.Object(id=GUILD_ID)

IMAGE_URL = "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/73256248-616c-4779-aa68-106c298d0710/dhkcje3-3cd29923-0668-4bec-9e12-a769ef2be017.jpg/v1/fill/w_1151,h_694,q_70,strp/cars_tvg_boxart_roblox_remake_by_redkirbdaredpuffball_dhkcje3-pre.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7ImhlaWdodCI6Ijw9Nzg0IiwicGF0aCI6Ii9mLzczMjU2MjQ4LTYxNmMtNDc3OS1hYTY4LTEwNmMyOThkMDcxMC9kaGtjamUzLTNjZDI5OTIzLTA2NjgtNGJlYy05ZTEyLWE3NjllZjJiZTAxNy5qcGciLCJ3aWR0aCI6Ijw9MTI5OSJ9XV0sImF1ZCI6WyJ1cm46c2VydmljZTppbWFnZS5vcGVyYXRpb25zIl19.hDvTXzd7zXPfY1NMj3QAIHT-LML9VDX9CbX98xCETTU"
ROLE_ID = 1434592997869228052

class SessionView(ui.View):
    def __init__(self, max_reactions: int, link: str):
        super().__init__(timeout=180)
        self.max_reactions = max_reactions
        self.link = link
        self.current_reactions = 0
        self.users = set()  # track who reacted

        self.react_button = ui.Button(label=f"React (0/{self.max_reactions})", style=ButtonStyle.primary)
        self.react_button.callback = self.react_callback
        self.add_item(self.react_button)

    async def react_callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        if user_id in self.users:
            self.users.remove(user_id)
            self.current_reactions -= 1
        else:
            self.users.add(user_id)
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

    embed = discord.Embed(title=title, description="React to join!", color=discord.Color.blue())
    embed.set_image(url=IMAGE_URL)
    embed.add_field(name="Location", value=location, inline=True)
    embed.add_field(name="Theme", value=theme, inline=True)

    view = SessionView(max_reactions=reactions, link=link)
    await channel.send(embed=embed, view=view)
    await interaction.response.send_message(f"Session sent in {channel.mention}", ephemeral=True)

@session.error
async def session_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message("You do not have permission to run this command.", ephemeral=True)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync(guild=GUILD)
        print(f'Synced {len(synced)} commands.')
    except Exception as e:
        print('Failed to sync commands:', e)
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('Slash commands synced!')

bot.run(os.environ['BOT_TOKEN'])

