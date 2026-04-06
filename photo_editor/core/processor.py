"""
core/processor.py
-----------------
Pure image-processing functions.  No Tkinter, no UI, no state.
All functions accept a PIL Image and return a new PIL Image.
"""

from PIL import Image, ImageDraw, ImageFilter


def apply_blur(image: Image.Image, radius: int) -> Image.Image:
    """Gaussian-style box blur.  radius=0 → no-op copy."""
    if radius > 0:
        return image.filter(ImageFilter.BoxBlur(radius))
    return image.copy()


def apply_contrast(image: Image.Image, factor: float) -> Image.Image:
    """Per-pixel contrast stretch around mid-grey (128)."""
    img = image.copy()
    pix = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b = pix[x, y]
            r = int((r - 128) * factor + 128)
            g = int((g - 128) * factor + 128)
            b = int((b - 128) * factor + 128)
            pix[x, y] = (_clamp(r), _clamp(g), _clamp(b))
    return img


def apply_grayscale(image: Image.Image, intensity: float) -> Image.Image:
    """Blend colour channels toward luminance-weighted grey.
    intensity=0.0 → full colour; 1.0 → full greyscale.
    """
    img = image.copy()
    pix = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b = pix[x, y]
            gray = int(r * 0.299 + g * 0.587 + b * 0.114)
            r = int(r * (1 - intensity) + gray * intensity)
            g = int(g * (1 - intensity) + gray * intensity)
            b = int(b * (1 - intensity) + gray * intensity)
            pix[x, y] = (_clamp(r), _clamp(g), _clamp(b))
    return img


def composite_draw_layer(base: Image.Image, stroke_layer, text_items: list) -> Image.Image:
    """Alpha-composite stroke layer then stamp text items over an RGB base."""
    from photo_editor.core.font_loader import get_font
    rgba_base = base.convert("RGBA")

    # 1. Pen/eraser strokes
    if stroke_layer is not None:
        rgba_base.paste(stroke_layer, mask=stroke_layer)

    # 2. Text items (rendered fresh — no ghost copies possible)
    if text_items:
        draw = ImageDraw.Draw(rgba_base)
        for item in text_items:
            rgba = hex_to_rgba(item["color"])
            font = get_font(item["font_size"], item["bold"])
            draw.text((item["x"], item["y"]), item["text"], fill=rgba, font=font)

    return rgba_base.convert("RGB")


def apply_pipeline(
    orig: Image.Image,
    stroke_layer,
    text_items: list,
    *,
    blur_radius: int,
    contrast_factor: float,
    grayscale_intensity: float,
) -> Image.Image:
    """Run the full filter pipeline in the correct order and return RGB."""
    img = apply_blur(orig, blur_radius)
    img = apply_contrast(img, contrast_factor)
    img = apply_grayscale(img, grayscale_intensity)
    img = composite_draw_layer(img, stroke_layer, text_items)
    return img


# ── Helpers ──────────────────────────────────────────────────────────────────

def _clamp(value: int, lo: int = 0, hi: int = 255) -> int:
    return max(lo, min(hi, value))


def hex_to_rgba(hex_color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i: i + 2], 16) for i in (0, 2, 4))
    return (r, g, b, alpha)
