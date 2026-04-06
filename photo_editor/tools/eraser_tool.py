"""
tools/eraser_tool.py
--------------------
Eraser that clears pixels on the RGBA draw layer.
No Tkinter dependency.
"""

from photo_editor.core.image_state import ImageState


class EraserTool:
    """Sets draw-layer pixels to transparent along a drag path."""

    def __init__(self, state: ImageState):
        self.state = state
        self._started = False

    def press(self, x: int, y: int) -> None:
        self.state.push_undo()
        self._started = True

    def drag(self, x0: int, y0: int, x1: int, y1: int, size: int) -> None:
        if not self._started or self.state.stroke_layer is None:
            return
        self._erase_stroke(x0, y0, x1, y1, size)

    def release(self) -> None:
        self._started = False

    # ── Internals ─────────────────────────────────────────────────────────────

    def _erase_stroke(self, x0: int, y0: int, x1: int, y1: int, size: int) -> None:
        r = max(size // 2, 1)
        dx, dy = x1 - x0, y1 - y0
        steps = max(abs(dx), abs(dy), 1)
        pix = self.state.stroke_layer.load()
        w, h = self.state.stroke_layer.size

        for i in range(steps + 1):
            t = i / steps
            cx = int(x0 + dx * t)
            cy = int(y0 + dy * t)
            for ox in range(-r, r + 1):
                for oy in range(-r, r + 1):
                    nx, ny = cx + ox, cy + oy
                    if 0 <= nx < w and 0 <= ny < h:
                        pix[nx, ny] = (0, 0, 0, 0)
