<div align="center">

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
Simply reply to a target message and mention the bot, and it will generate a memorial image.

## Key Features

- **Reply-only trigger**
  - Reply to a message and mention the bot to instantly create an image for that replied message.
- **Profile Picture Rendering**
  - The target user’s avatar is embedded in the memorial image.
- **Dynamic Image Generation**
  - Real-time canvas rendering using the `Pillow` library.
  - The message is rendered below the avatar with automatic wrapping and center alignment.
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
The bot auto-detects a Korean-capable system font on macOS and falls back to a font in `assets/fonts/` if you provide one there.
If you want to override the default, place a `.ttf` or `.ttc` font file in `assets/fonts/` and name it `malgun.ttf`, or update `image_generator.py` to point at your preferred font.

### 4. Run
```bash
python bot.py
```
