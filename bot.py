import os
import io
import discord
from discord import app_commands
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int):
    lines = []
    words = text.split()
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        if font.getlength(test_line) <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line.strip())
            current_line = word + " "
            
    if current_line:
        lines.append(current_line.strip())

    return lines

def generate_funeral_image(author_name: str, message_content: str):
    canvas = Image.new("RGB", (800, 1000), (20, 20, 20))
    draw = ImageDraw.Draw(canvas)
    
    draw.rectangle([(20, 20), (780, 980)], outline=(100, 100, 100), width=10)
    
    draw.polygon([(20, 20), (120, 20), (20, 120)], fill=(0, 0, 0))
    draw.polygon([(780, 20), (680, 20), (780, 120)], fill=(0, 0, 0))
    
    try:
        font_title = ImageFont.truetype("malgun.ttf", 60)
        font_content = ImageFont.truetype("malgun.ttf", 45)
        font_bottom = ImageFont.truetype("malgun.ttf", 40)
    except IOError:
        font_title = ImageFont.load_default(size=60)
        font_content = ImageFont.load_default(size=45)
        font_bottom = ImageFont.load_default(size=40)
        
    draw.text((400, 150), f"故 {author_name}", fill=(255, 255, 255), font=font_title, anchor="mm")
    draw.text((400, 900), "삼가 고인의 명복을 빕니다", fill=(200, 200, 200), font=font_bottom, anchor="mm")
    
    wrapped_lines = wrap_text(f'"{message_content}"', font_content, 700)
    
    total_text_height = len(wrapped_lines) * 60
    y_offset = (1000 - total_text_height) // 2
    
    for line in wrapped_lines:
        draw.text((400, y_offset), line, fill=(255, 255, 255), font=font_content, anchor="mm")
        y_offset += 60
        
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
    await interaction.response.defer()
    
    canvas = generate_funeral_image(message.author.display_name, message.content)
    
    buffer = io.BytesIO()
    canvas.save(buffer, format="PNG")
    buffer.seek(0)
    
    file = discord.File(buffer, filename="funeral.png")
    await interaction.followup.send(file=file)

if __name__ == "__main__":
    client.run(TOKEN)
