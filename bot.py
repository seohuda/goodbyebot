from image_generator import generate_funeral_image
import os
import io
import discord
from config import TOKEN

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
