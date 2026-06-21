import os
import discord
from discord import app_commands
from dotenv import load_dotenv
from PIL import Image

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

def create_base_canvas():
    canvas = Image.new("RGB", (800, 1000), (20, 20, 20))
    return canvas

class FuneralClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

    async def on_ready(self):
        pass

client = FuneralClient()

@client.tree.context_menu(
    name="장례식 치르기",
    allowed_installs=app_commands.AppInstallationType(user=True),
    allowed_contexts=app_commands.AppCommandContext(guild=True, bot_dm=True, private_channel=True)
)
async def funeral_menu(interaction: discord.Interaction, message: discord.Message):
    canvas = create_base_canvas()
    await interaction.response.send_message("준비 중...", ephemeral=True)

if __name__ == "__main__":
    client.run(TOKEN)
