"""
tools/tool_manager.py
---------------------
Owns all drawing-tool instances and routes mouse events to the active tool.
Knows nothing about Tkinter widgets — it receives plain (x, y) integers.
"""

from photo_editor.core.image_state import ImageState
from photo_editor.tools.pen_tool import PenTool
from photo_editor.tools.eraser_tool import EraserTool
from photo_editor.tools.text_tool import TextTool
from photo_editor.tools.move_tool import MoveTextTool

TOOL_NONE      = "none"
TOOL_PEN       = "pen"
TOOL_ERASER    = "eraser"
TOOL_TEXT      = "text"
TOOL_MOVE_TEXT = "move_text"

ALL_TOOLS = (TOOL_NONE, TOOL_PEN, TOOL_ERASER, TOOL_TEXT, TOOL_MOVE_TEXT)


class ToolManager:
    """Routes press / drag / release / text events to the active tool."""

    def __init__(self, state: ImageState):
        self._state     = state
        self._pen       = PenTool(state)
        self._eraser    = EraserTool(state)
        self._text      = TextTool(state)
        self._move_text = MoveTextTool(state)
        self.active     = TOOL_NONE

        # Shared drawing parameters (set by the UI layer)
        self.color     : str  = "#ff4444"
        self.pen_size  : int  = 3
        self.font_size : int  = 24
        self.bold      : bool = False

    # ── Active-tool switching ─────────────────────────────────────────────────

    def set_tool(self, tool: str) -> None:
        if tool not in ALL_TOOLS:
            raise ValueError(f"Unknown tool '{tool}'. Valid: {ALL_TOOLS}")
        self.active = tool

    # ── Event routing ─────────────────────────────────────────────────────────

    def on_press(self, x: int, y: int) -> bool:
        """Returns True when the caller should schedule a canvas refresh."""
        if not self._state.is_ready():
            return False
        if self.active == TOOL_PEN:
            self._pen.press(x, y)
        elif self.active == TOOL_ERASER:
            self._eraser.press(x, y)
        elif self.active == TOOL_MOVE_TEXT:
            return self._move_text.press(x, y)
        return False

    def on_drag(self, x0: int, y0: int, x1: int, y1: int) -> bool:
        """Returns True when caller should schedule a canvas refresh."""
        if not self._state.is_ready():
            return False
        if self.active == TOOL_PEN:
            self._pen.drag(x0, y0, x1, y1, self.color, self.pen_size)
            return True
        if self.active == TOOL_ERASER:
            self._eraser.drag(x0, y0, x1, y1, self.pen_size)
            return True
        if self.active == TOOL_MOVE_TEXT:
            return self._move_text.drag(x1, y1)
        return False

    def on_release(self, x: int, y: int) -> None:
        if self.active == TOOL_PEN:
            self._pen.release()
        elif self.active == TOOL_ERASER:
            self._eraser.release()
        elif self.active == TOOL_MOVE_TEXT:
            self._move_text.release()

    def place_text(self, x: int, y: int, text: str) -> bool:
        """Place text at (x, y). Returns True on success."""
        if not self._state.is_ready() or not text:
            return False
        self._text.place(x, y, text, self.color, self.font_size, self.bold)
        return True
