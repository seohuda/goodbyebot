from PIL import ImageFont

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
