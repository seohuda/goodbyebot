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
