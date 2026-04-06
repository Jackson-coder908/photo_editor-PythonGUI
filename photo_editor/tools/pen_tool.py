"""
tools/pen_tool.py
-----------------
Freehand pen stroke logic.  Operates directly on an ImageState draw layer.
No Tkinter dependency.
"""

from PIL import ImageDraw
from photo_editor.core.image_state import ImageState
from photo_editor.core.processor import hex_to_rgba


class PenTool:
    """Draws anti-aliased line segments onto the draw layer."""

    def __init__(self, state: ImageState):
        self.state = state
        self._started = False

    def press(self, x: int, y: int) -> None:
        self.state.push_undo()
        self._started = True

    def drag(self, x0: int, y0: int, x1: int, y1: int,
             color: str, size: int) -> None:
        if not self._started or self.state.stroke_obj is None:
            return
        rgba = hex_to_rgba(color)
        r = max(size // 2, 1)
        self.state.stroke_obj.line([x0, y0, x1, y1], fill=rgba, width=size)
        self.state.stroke_obj.ellipse([x1 - r, y1 - r, x1 + r, y1 + r], fill=rgba)

    def release(self) -> None:
        self._started = False
