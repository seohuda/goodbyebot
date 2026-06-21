import os
import discord
from discord import app_commands
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

def create_base_canvas(author_name: str):
    canvas = Image.new("RGB", (800, 1000), (20, 20, 20))
    draw = ImageDraw.Draw(canvas)
    
    draw.rectangle([(20, 20), (780, 980)], outline=(100, 100, 100), width=10)
    
    draw.polygon([(20, 20), (120, 20), (20, 120)], fill=(0, 0, 0))
    draw.polygon([(780, 20), (680, 20), (780, 120)], fill=(0, 0, 0))
    
    try:
        font_title = ImageFont.truetype("malgun.ttf", 60)
        font_bottom = ImageFont.truetype("malgun.ttf", 40)
    except IOError:
        font_title = ImageFont.load_default(size=60)
        font_bottom = ImageFont.load_default(size=40)
        
    draw.text((400, 150), f"故 {author_name}", fill=(255, 255, 255), font=font_title, anchor="mm")
    draw.text((400, 900), "삼가 고인의 명복을 빕니다", fill=(200, 200, 200), font=font_bottom, anchor="mm")
    
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
    canvas, draw = create_base_canvas(message.author.display_name)
    await interaction.response.send_message("준비 중...", ephemeral=True)

if __name__ == "__main__":
    client.run(TOKEN)
