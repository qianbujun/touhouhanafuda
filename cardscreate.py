from PIL import Image, ImageDraw, ImageFont
import os
from card import card

# 卡牌尺寸配置
CARD_WIDTH = 100
CARD_HEIGHT = 150
BACKGROUND_COLOR = (255, 255, 255)  # 白色背景
TEXT_COLOR = (0, 0, 0)  # 黑色文字
FONT_SIZE = 20
LINE_SPACING = 5  # 行间距
MAX_CHARS_PER_LINE = 4  # 每行最多显示4个字符
OUTPUT_DIR = "assets/cards"

def split_text(text, max_chars_per_line):
    """将文本按每max_chars_per_line个字符进行分段"""
    return [text[i:i+max_chars_per_line] for i in range(0, len(text), max_chars_per_line)]

def create_card_image(card_name):
    """创建单张卡牌图片，支持多行显示"""
    img = Image.new('RGB', (CARD_WIDTH, CARD_HEIGHT), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)

    # 加载字体
    try:
        font_path = "simhei.ttf"  # Windows 中文字体
        font = ImageFont.truetype(font_path, FONT_SIZE)
    except:
        try:
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"  # Linux 字体
            font = ImageFont.truetype(font_path, FONT_SIZE)
        except:
            font = ImageFont.load_default()
            print("⚠️ 使用默认字体（可能不支持中文）")

    # 分割文本
    lines = split_text(card_name, MAX_CHARS_PER_LINE)

    # 计算总高度
    total_height = 0
    line_heights = []
    for line in lines:
        bbox = font.getbbox(line)
        line_height = bbox[3] - bbox[1]
        line_heights.append(line_height)
        total_height += line_height + LINE_SPACING
    total_height -= LINE_SPACING  # 最后一行不加行间距

    # 计算起始 y 坐标
    y = (CARD_HEIGHT - total_height) / 2

    # 逐行绘制
    for line, height in zip(lines, line_heights):
        bbox = font.getbbox(line)
        text_width = bbox[2] - bbox[0]
        x = (CARD_WIDTH - text_width) / 2
        draw.text((x, y), line, fill=TEXT_COLOR, font=font)
        y += height + LINE_SPACING

    return img

def generate_all_cards():
    """生成所有卡牌图片"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    all_cards = card.initialize_cards()

    for c in all_cards:
        img = create_card_image(c.name)
        filename = f"{c.name}.png"
        filepath = os.path.join(OUTPUT_DIR, filename)
        img.save(filepath)
        print(f"✅ 已生成: {filename}")

if __name__ == "__main__":
    generate_all_cards()
