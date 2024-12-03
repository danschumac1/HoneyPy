import os
import raylibpy as rl

def load_font(font_name: str = "joystix monospace.otf", font_dir: str = "resources/font") -> rl.Font:
    font_path = os.path.join(os.getcwd(), font_dir, font_name)
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"Font file not found at: {font_path}")
    try:
        return rl.load_font(font_path)
    except Exception as e:
        raise RuntimeError(f"Failed to load font from {font_path}: {e}")

def unload_font(font):
    rl.unload_font(font)

def draw_centered_text(font, text, font_size, y_position, width, color=rl.BLACK):
    text_len = rl.measure_text_ex(font, text, font_size, 0).x
    rl.draw_text_ex(
        font=font,
        text=text,
        position=rl.Vector2(width // 2 - text_len // 2, y_position),
        font_size=font_size,
        spacing=0,
        tint=color,
    )
