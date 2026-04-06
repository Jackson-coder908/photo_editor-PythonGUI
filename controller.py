"""
controller.py
-------------
Application controller.  Wires together all UI widgets, the ImageState,
the ToolManager, and the processing pipeline.

This is the only file that knows about *all* the other modules.
"""

import os
import tkinter as tk
from tkinter import filedialog, simpledialog
from PIL import Image

from photo_editor.core.image_state import ImageState
from photo_editor.core.processor   import apply_pipeline
from photo_editor.tools.tool_manager import ToolManager, TOOL_TEXT, TOOL_MOVE_TEXT
from photo_editor.ui.toolbar     import Toolbar
from photo_editor.ui.canvas_view import CanvasView
from photo_editor.ui.side_panel  import SidePanel
from photo_editor.ui.status_bar  import StatusBar


class PhotoEditorApp:
    MAX_SIZE = (1920, 1080)

    def __init__(self, root: tk.Tk):
        self.root  = root
        self.state = ImageState()
        self.tools = ToolManager(self.state)
        self._render_job = None

        root.title("Python RGB Master Editor")
        root.configure(bg="#1a1a2e")
        root.minsize(800, 560)

        self._build_ui()

    # ── UI assembly ───────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        # Status bar (pack bottom first so it doesn't get squeezed)
        self.status = StatusBar(self.root)
        self.status.pack(fill=tk.X, side=tk.BOTTOM)

        # Toolbar
        Toolbar(
            self.root,
            on_open=self._open,
            on_save=self._save,
            on_clear=self._clear,
            on_undo=self._undo,
        ).pack(fill=tk.X)

        # Main area
        main = tk.Frame(self.root, bg="#1a1a2e")
        main.pack(fill=tk.BOTH, expand=True)

        # Canvas
        self.canvas_view = CanvasView(
            main,
            on_press=self._on_press,
            on_drag=self._on_drag,
            on_release=self._on_release,
        )
        self.canvas_view.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Side panel
        self.panel = SidePanel(
            main,
            on_tool_change=self._on_tool_change,
            on_filter_change=self._render,
        )
        self.panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 8), pady=8)

    # ── File operations ───────────────────────────────────────────────────────

    def _open(self) -> None:
        path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")])
        if not path:
            return
        img = Image.open(path).convert("RGBA")
        img.thumbnail(self.MAX_SIZE, Image.Resampling.LANCZOS)
        self.state.load(img)
        self._render()
        self.status.set(f"Loaded: {os.path.basename(path)}  ({img.width}×{img.height})")

    def _save(self) -> None:
        if self.state.orig is None:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("All files", "*.*")])
        if path:
            self._current_display().save(path)
            self.status.set(f"Saved → {path}")

    # ── Drawing callbacks (delegated to ToolManager) ──────────────────────────

    def _on_tool_change(self, name: str) -> None:
        self.tools.set_tool(name)
        self.panel.highlight_tool(name)
        hints = {
            "pen":       "✏ Pen active – click & drag to draw",
            "eraser":    "⬜ Eraser active – drag to erase",
            "text":      "T  Text active – click where to place text",
            "move_text": "↖ Move Text – click a text label and drag it",
            "none":      "No tool selected",
        }
        self.status.set(hints.get(name, ""))

    def _on_press(self, x: int, y: int) -> None:
        self._sync_tool_params()
        if self.tools.active == TOOL_TEXT:
            text = simpledialog.askstring("Add Text", "Enter text:", parent=self.root)
            if self.tools.place_text(x, y, text or ""):
                self._render()
                self.status.set(f'Text "{text}" placed at ({x}, {y})')
        else:
            self.tools.on_press(x, y)

    def _on_drag(self, x0: int, y0: int, x1: int, y1: int) -> None:
        if self.tools.on_drag(x0, y0, x1, y1):
            self._render()

    def _on_release(self, x: int, y: int) -> None:
        self.tools.on_release(x, y)

    # ── Edit operations ───────────────────────────────────────────────────────

    def _clear(self) -> None:
        if self.state.is_ready():
            self.state.clear_draw_layer()
            self._render()
            self.status.set("Drawing cleared.")

    def _undo(self) -> None:
        if self.state.pop_undo():
            self._render()
            self.status.set("Undo applied.")
        else:
            self.status.set("Nothing to undo.")

    # ── Rendering ─────────────────────────────────────────────────────────────

    def _sync_tool_params(self) -> None:
        """Push current panel values into the ToolManager."""
        self.tools.color     = self.panel.pen_color
        self.tools.pen_size  = self.panel.pen_size
        self.tools.font_size = self.panel.font_size
        self.tools.bold      = self.panel.bold

    def _render(self) -> None:
        """Debounce rendering to avoid UI freezes."""
        if self._render_job is not None:
            self.root.after_cancel(self._render_job)
        self._render_job = self.root.after(15, self._render_now)

    def _render_now(self) -> None:
        """Rebuild the display image from scratch and push it to the canvas."""
        self._render_job = None
        if not self.state.is_ready():
            return
        self._sync_tool_params()
        result = apply_pipeline(
            self.state.orig,
            self.state.stroke_layer,
            self.state.text_items,
            blur_radius=self.panel.blur,
            contrast_factor=self.panel.contrast,
            grayscale_intensity=self.panel.grayscale,
        )
        self.canvas_view.show(result)
        self._last_result = result

    def _current_display(self) -> Image.Image:
        return getattr(self, "_last_result", self.state.orig)
