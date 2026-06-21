import os
import discord
from discord import app_commands
from dotenv import load_dotenv
from PIL import Image, ImageDraw

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

def create_base_canvas():
    canvas = Image.new("RGB", (800, 1000), (20, 20, 20))
    draw = ImageDraw.Draw(canvas)
    
    draw.rectangle([(20, 20), (780, 980)], outline=(100, 100, 100), width=10)
    
    draw.polygon([(20, 20), (120, 20), (20, 120)], fill=(0, 0, 0))
    draw.polygon([(780, 20), (680, 20), (780, 120)], fill=(0, 0, 0))
    
    return canvas, draw

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
    canvas, draw = create_base_canvas()
    await interaction.response.send_message("준비 중...", ephemeral=True)

if __name__ == "__main__":
    client.run(TOKEN)
