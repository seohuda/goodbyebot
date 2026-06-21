<div align="center">

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
git clone https://github.com/your-username/goodbyebot.git
cd goodbyebot
pip install -r requirements.txt
echo "DISCORD_TOKEN=your_bot_token_here" > .env
```

### 3. 필수 에셋
코드 내에서 `malgun.ttf` (맑은 고딕) 폰트를 참조하고 있습니다. 
프로젝트 루트 디렉토리에 사용할 `.ttf` 폰트 파일을 배치하거나, 코드 내부의 폰트 파일명을 환경에 맞게 수정하세요.

### 4. 실행
```bash
python bot.py
```
