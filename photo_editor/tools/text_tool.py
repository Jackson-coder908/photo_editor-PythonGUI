"""
tools/text_tool.py
------------------
Registers text items in state.text_items (metadata only).
Actual pixel rendering happens in processor.composite_draw_layer()
so text is always drawn fresh — moving it never creates ghost copies.
"""

from photo_editor.core.image_state import ImageState


class TextTool:
    def __init__(self, state: ImageState):
        self.state = state

    def place(self, x: int, y: int, text: str,
              color: str, font_size: int, bold: bool = False) -> None:
        if not text or not self.state.is_ready():
            return
        self.state.push_undo()
        self.state.text_items.append({
            "text": text, "x": x, "y": y,
            "color": color, "font_size": font_size, "bold": bold,
        })
