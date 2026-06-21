import os
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
