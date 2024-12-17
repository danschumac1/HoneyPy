import os
import raylibpy as rl

def load_font(font_name: str = "joystix monospace.otf", font_dir: str = "resources/font") -> rl.Font:
    """
    Loads a font from the specified directory.

    Args:
        font_name (str): The name of the font file to load. Defaults to "joystix monospace.otf".
        font_dir (str): The directory where the font file is located. Defaults to "resources/font".

    Returns:
        rl.Font: The loaded font object.

    Raises:
        FileNotFoundError: If the font file does not exist at the specified path.
        RuntimeError: If there is an error loading the font.
    """
    font_path = os.path.join(os.getcwd(), font_dir, font_name)
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"Font file not found at: {font_path}")
    try:
        return rl.load_font(font_path)
    except Exception as e:
        raise RuntimeError(f"Failed to load font from {font_path}: {e}")

def draw_centered_text(font, text, font_size, y_position, width, color=rl.BLACK):
    """
    Draws text centered horizontally on the screen.

    Args:
        font (rl.Font): The font to use for the text.
        text (str): The text to be drawn.
        font_size (float): The size of the font.
        y_position (float): The y-coordinate position to draw the text.
        width (int): The width of the area to center the text within.
        color (rl.Color, optional): The color of the text. Defaults to rl.BLACK.

    Returns:
        None
    """
    text_len = rl.measure_text_ex(font, text, font_size, 0).x
    rl.draw_text_ex(
        font=font,
        text=text,
        position=rl.Vector2(width // 2 - text_len // 2, y_position),
        font_size=font_size,
        spacing=0,
        tint=color,
    )
