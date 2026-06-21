import os
import subprocess
import re

# 1. Update requirements.txt
with open("requirements.txt", "w") as f:
    f.write("discord.py>=2.4.0\n")
    f.write("Pillow>=10.4.0\n")
    f.write("python-dotenv>=1.0.1\n")

# 2. Fix bot.py
with open("bot.py", "w") as f:
    f.write("""import io
import discord
from config import TOKEN
from image_generator import generate_funeral_image

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

            # 예외 처리 1: 첨부파일이나 임베드만 있는 경우
            if not target_message.content and (target_message.attachments or target_message.embeds):
                await message.channel.send("텍스트 메시지만 영정사진으로 만들 수 있습니다.", reference=message)
                return

            content = target_message.clean_content
            if target_message == message:
                content = content.replace(f'@{self.user.display_name}', '').strip()
                content = content.replace(f'@{self.user.name}', '').strip()
                
            if not content:
                content = "(내용 없음)"

            # 예외 처리 2: 너무 긴 메시지 자르기
            if len(content) > 150:
                content = content[:147] + "..."

            try:
                canvas = generate_funeral_image(target_message.author.display_name, content)
                
                buffer = io.BytesIO()
                canvas.save(buffer, format="PNG")
                buffer.seek(0)
                
                file = discord.File(buffer, filename="funeral.png")
                await message.channel.send(file=file, reference=message)
            except IOError:
                await message.channel.send("폰트 파일을 찾을 수 없어 기본 폰트로 렌더링되었습니다. (한글이 깨질 수 있습니다)", reference=message)
            except Exception as e:
                print(f"Error: {e}")
                await message.channel.send("이미지 생성 중 오류가 발생했습니다.", reference=message)

client = FuneralClient()

if __name__ == "__main__":
    if not TOKEN:
        print("Error: DISCORD_TOKEN is not set in .env file.")
    else:
        client.run(TOKEN)
""")

# 3. Fix config.py
with open("config.py", "w") as f:
    f.write("""import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
""")

# 4. Fix image_generator.py
with open("image_generator.py", "w") as f:
    f.write("""import os
from PIL import Image, ImageDraw, ImageFont
from text_utils import wrap_text

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "fonts")

def generate_funeral_image(author_name: str, message_content: str):
    canvas = Image.new("RGB", (800, 1000), (20, 20, 20))
    draw = ImageDraw.Draw(canvas)
    
    draw.rectangle([(20, 20), (780, 980)], outline=(100, 100, 100), width=10)
    
    draw.polygon([(20, 20), (120, 20), (20, 120)], fill=(0, 0, 0))
    draw.polygon([(780, 20), (680, 20), (780, 120)], fill=(0, 0, 0))
    
    font_path = os.path.join(FONT_DIR, "malgun.ttf")
    try:
        font_title = ImageFont.truetype(font_path, 60)
        font_content = ImageFont.truetype(font_path, 45)
        font_bottom = ImageFont.truetype(font_path, 40)
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
""")

# 5. Fix text_utils.py
with open("text_utils.py", "w") as f:
    f.write("""from PIL import ImageFont

def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int):
    lines = []
    current_line = ""
    
    for char in text:
        test_line = current_line + char
        if font.getlength(test_line) <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = char
            
    if current_line:
        lines.append(current_line)
        
    return lines
""")

# 6. Fix READMEs
with open("README.md", "w") as f:
    f.write("""<div align="center">

# Rest in Peace Bot
**A Discord Bot for Memorializing Messages**<br>

[Read in Korean (한국어로 읽기)](README_kr.md)

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Discord.py](https://img.shields.io/badge/discord.py-2.4+-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discordpy.readthedocs.io/)
[![Pillow](https://img.shields.io/badge/Pillow-Image_Processing-FFD43B?style=for-the-badge&logo=python&logoColor=darkblue)](https://python-pillow.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

</div>

<br>

## Introduction

Turn any memorable message into a "funeral portrait".
Simply reply to a target message and mention the bot, or mention the bot in your own message, and it will generate a memorial image.

## Key Features

- **Mention Support**
  - Reply to a message and mention the bot to instantly create an image for that message.
- **Dynamic Image Generation**
  - Real-time canvas rendering using the `Pillow` library.
  - Intelligent auto word-wrap and center alignment based on font length.
- **Memory Buffer Transfer**
  - Direct transmission to the Discord server via `io.BytesIO` buffer without saving the image to disk.

## Installation & Usage

### 1. Prerequisites
- Python 3.10 or higher
- Create a bot in the Discord Developer Portal and enable the `Message Content Intent`.

### 2. Setup
```bash
git clone https://github.com/seohuda/goodbyebot.git
cd goodbyebot
pip install -r requirements.txt
echo "DISCORD_TOKEN=your_bot_token_here" > .env
```

### 3. Assets Required
The code references the `malgun.ttf` font. 
Place a `.ttf` font file in `assets/fonts/` directory, or modify the font file name in the code to match your environment.

### 4. Run
```bash
python bot.py
```
""")

with open("README_kr.md", "w") as f:
    f.write("""<div align="center">

# 장례식 봇 (Rest in Peace Bot)
**유언을 영정사진으로 만들어주는 디스코드 봇**<br>

[Read in English (영어로 읽기)](README.md)

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Discord.py](https://img.shields.io/badge/discord.py-2.4+-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discordpy.readthedocs.io/)
[![Pillow](https://img.shields.io/badge/Pillow-Image_Processing-FFD43B?style=for-the-badge&logo=python&logoColor=darkblue)](https://python-pillow.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

</div>

<br>

## 소개

디스코드에서 남긴 레전드 메시지를 영정사진으로 만들어 박제하세요.
원하는 메시지에 답장하며 봇을 멘션하거나, 자신의 메시지에 봇을 멘션하면 합성 이미지를 생성해 줍니다.

## 주요 기능

- **멘션 인식**
  - 메시지에 답장하며 봇을 멘션(`@봇이름`)하면 즉시 실행됩니다.
- **동적 이미지 생성**
  - `Pillow` 라이브러리를 활용한 실시간 캔버스 렌더링.
  - 폰트 길이를 계산한 지능형 자동 줄바꿈(Word Wrap) 및 중앙 정렬 알고리즘 적용.
- **메모리 버퍼 전송**
  - 이미지를 디스크에 저장하지 않고 `io.BytesIO` 버퍼를 통해 서버로 다이렉트 전송.

## 설치 및 실행

### 1. 필수 조건
- Python 3.10 이상
- 디스코드 개발자 포털에서 봇 생성 및 `Message Content Intent` 활성화

### 2. 환경 설정
```bash
git clone https://github.com/seohuda/goodbyebot.git
cd goodbyebot
pip install -r requirements.txt
echo "DISCORD_TOKEN=your_bot_token_here" > .env
```

### 3. 필수 에셋
코드 내에서 `malgun.ttf` (맑은 고딕) 폰트를 참조하고 있습니다. 
`assets/fonts/` 폴더에 `.ttf` 폰트 파일을 배치하거나, 코드 내부의 폰트 파일명을 환경에 맞게 수정하세요.

### 4. 실행
```bash
python bot.py
```
""")

subprocess.run(["git", "add", "."])
subprocess.run(["git", "commit", "-m", "fix: resolve syntax issues and improve error handling"])
