from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parents[1] / "docs" / "assets" / "holocore-demo.gif"
W, H = 960, 540
bg = (5, 14, 31)
cyan = (41, 211, 255)
green = (91, 235, 126)
white = (235, 243, 255)
muted = (154, 177, 207)
navy = (12, 29, 55)

def font(size, bold=False):
    name = "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"
    return ImageFont.truetype(name, size)

def frame(step, title, subtitle, active):
    im = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(im)
    for x in range(0, W, 48): d.line((x, 0, x, H), fill=(8, 25, 48), width=1)
    for y in range(0, H, 48): d.line((0, y, W, y), fill=(8, 25, 48), width=1)
    d.text((42, 28), "HOLOCORE", font=font(28, True), fill=cyan)
    d.text((42, 72), title, font=font(38, True), fill=white)
    d.text((42, 122), subtitle, font=font(20), fill=muted)
    labels = [("ASK", 75, "?"), ("ATLAS", 260, "A"), ("ARCHIVE", 470, "✓"), ("ANIMUS", 680, "✦"), ("AI", 850, "H")]
    for i, (label, x, symbol) in enumerate(labels):
        color = cyan if i == active else (65, 87, 121)
        d.rounded_rectangle((x-55, 255, x+55, 365), radius=18, outline=color, width=4, fill=navy)
        d.text((x, 286), symbol, anchor="mm", font=font(38, True), fill=color)
        d.text((x, 395), label, anchor="mm", font=font(16, True), fill=color)
        if i < len(labels)-1:
            d.line((x+62, 310, labels[i+1][1]-62, 310), fill=green if i < active else (48, 68, 99), width=5)
            d.polygon([(labels[i+1][1]-70,300),(labels[i+1][1]-55,310),(labels[i+1][1]-70,320)], fill=green if i < active else (48,68,99))
    d.rounded_rectangle((42, 465, 918, 505), radius=12, fill=(10, 34, 57), outline=(17, 92, 129), width=2)
    d.text((480, 485), "Relevant knowledge — not the whole project history", anchor="mm", font=font(18, True), fill=green)
    return im

frames = [
    frame(0, "Ask once", "Start with the task you want the AI to solve.", 0),
    frame(1, "Route once", "HoloCore checks the structural map first.", 1),
    frame(2, "Select what matters", "Verified Archive knowledge is added next.", 2),
    frame(3, "Recall history only when needed", "Animus supplies relevant remembered context.", 3),
    frame(4, "Send focused context", "The AI receives a smaller, useful context window.", 4),
]
OUT.parent.mkdir(parents=True, exist_ok=True)
frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=1200, loop=0, optimize=True)
print(OUT)
