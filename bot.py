import os
import io
import discord
from PIL import Image, ImageDraw, ImageFont
from text_utils import wrap_text

from config import TOKEN

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
    
    if len(message_content) > 150:
        message_content = message_content[:147] + "..."
        
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
        intents.message_content = True
        super().__init__(intents=intents)

    async def on_ready(self):
        print(f"Logged in as {self.user}")

    async def on_message(self, message):
        if message.author.bot:
            return
        
        if self.user.mentioned_in(message):
            target_message = message
            if message.reference and isinstance(message.reference.resolved, discord.Message):
                target_message = message.reference.resolved

            content = target_message.clean_content
            if target_message == message:
                content = content.replace(f'@{self.user.display_name}', '').strip()
                content = content.replace(f'@{self.user.name}', '').strip()
                
            if not content:
                content = "(내용 없음)"

            try:
                canvas = generate_funeral_image(target_message.author.display_name, content)
                
                buffer = io.BytesIO()
                canvas.save(buffer, format="PNG")
                buffer.seek(0)
                
                file = discord.File(buffer, filename="funeral.png")
                await message.channel.send(file=file, reference=message)
            except Exception as e:
                print(f"Error: {e}")
                await message.channel.send("이미지 생성 중 오류가 발생했습니다.", reference=message)

client = FuneralClient()

if __name__ == "__main__":
    if not TOKEN:
        print("Error: DISCORD_TOKEN is not set in .env file.")
    else:
        client.run(TOKEN)
