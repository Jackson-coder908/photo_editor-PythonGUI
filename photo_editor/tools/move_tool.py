"""
tools/move_tool.py
------------------
Moves a placed text item by updating its (x, y) in state.text_items.
No pixel manipulation needed — the processor re-renders text from metadata
on every frame, so there are never any ghost copies.
"""

from __future__ import annotations
from photo_editor.core.image_state import ImageState

HIT_RADIUS = 150  # Manhattan-distance pixels to "grab" a text item


class MoveTextTool:
    def __init__(self, state: ImageState):
        self.state = state
        self._dragging_idx: int | None = None
        self._drag_offset: tuple[int, int] = (0, 0)

    def press(self, x: int, y: int) -> bool:
        """Grab the nearest text item within HIT_RADIUS. Returns True if grabbed."""
        best_idx, best_dist = None, HIT_RADIUS + 1
        for i, item in enumerate(self.state.text_items):
            dist = abs(item["x"] - x) + abs(item["y"] - y)
            if dist < best_dist:
                best_dist = dist
                best_idx = i

        if best_idx is not None:
            self.state.push_undo()
            self._dragging_idx = best_idx
            item = self.state.text_items[best_idx]
            self._drag_offset = (item["x"] - x, item["y"] - y)
            return True
        return False

    def drag(self, x: int, y: int) -> bool:
        """Update grabbed item's position. Returns True to trigger re-render."""
        if self._dragging_idx is None:
            return False
        item = self.state.text_items[self._dragging_idx]
        item["x"] = x + self._drag_offset[0]
        item["y"] = y + self._drag_offset[1]
        return True

    def release(self) -> None:
        self._dragging_idx = None

    def is_dragging(self) -> bool:
        return self._dragging_idx is not None
