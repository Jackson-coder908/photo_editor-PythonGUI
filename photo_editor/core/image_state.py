"""
core/image_state.py
-------------------
Holds all mutable image data: the original image, the transparent draw
overlay, and the undo history.  No Tkinter dependency.

Two-layer design
────────────────
  stroke_layer  — RGBA, pen/eraser pixels only, never contains text
  text_items    — list of dicts describing each text label (metadata only)

The final composited draw_layer (stroke_layer + text stamps) is assembled
by the processor at render time, so moving text never causes ghost copies.
"""

from PIL import Image, ImageDraw


class ImageState:
    """Single source of truth for all image data."""

    MAX_UNDO = 30

    def __init__(self):
        self.orig: Image.Image | None = None

        # ── Two separate layers ───────────────────────────────────────────────
        # Pen/eraser strokes only — text is NEVER painted here
        self.stroke_layer: Image.Image | None = None
        self.stroke_obj:   ImageDraw.ImageDraw | None = None

        # Text metadata — rendered fresh on every composite
        # Each entry: {"text", "x", "y", "color", "font_size", "bold"}
        self.text_items: list[dict] = []

        self._undo_stack: list[tuple] = []  # (stroke_layer copy, text_items copy)

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def load(self, pil_image: Image.Image) -> None:
        self.orig = pil_image.convert("RGB")
        self._reset_layers()
        self._undo_stack.clear()

    def is_ready(self) -> bool:
        return self.orig is not None

    # ── Layer management ──────────────────────────────────────────────────────

    def _reset_layers(self) -> None:
        self.stroke_layer = Image.new("RGBA", self.orig.size, (0, 0, 0, 0))
        self.stroke_obj   = ImageDraw.Draw(self.stroke_layer)
        self.text_items   = []

    def clear_draw_layer(self) -> None:
        """Wipe strokes and text (with undo support)."""
        self.push_undo()
        self._reset_layers()

    # ── Undo ──────────────────────────────────────────────────────────────────

    def push_undo(self) -> None:
        if self.stroke_layer is None:
            return
        self._undo_stack.append((
            self.stroke_layer.copy(),
            [t.copy() for t in self.text_items],
        ))
        if len(self._undo_stack) > self.MAX_UNDO:
            self._undo_stack.pop(0)

    def pop_undo(self) -> bool:
        if not self._undo_stack:
            return False
        self.stroke_layer, self.text_items = self._undo_stack.pop()
        self.stroke_obj = ImageDraw.Draw(self.stroke_layer)
        return True

    def can_undo(self) -> bool:
        return bool(self._undo_stack)
