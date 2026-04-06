"""
ui/canvas_view.py
-----------------
Wraps the Tkinter Canvas.  Handles image display and routes raw mouse events
to higher-level callbacks supplied by the controller.
"""

import tkinter as tk
from PIL import ImageTk, Image


class CanvasView(tk.Frame):
    def __init__(
        self,
        parent,
        on_press,
        on_drag,
        on_release,
        **kwargs,
    ):
        super().__init__(parent, bg="#1a1a2e", **kwargs)

        self.canvas = tk.Canvas(
            self,
            bg="#0d0d1a",
            cursor="crosshair",
            highlightthickness=1,
            highlightbackground="#533483",
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self._on_press   = on_press
        self._on_drag    = on_drag
        self._on_release = on_release

        self.canvas.bind("<ButtonPress-1>",   self._press)
        self.canvas.bind("<B1-Motion>",       self._drag)
        self.canvas.bind("<ButtonRelease-1>", self._release)
        self.canvas.bind("<Configure>",       self._on_resize)

        self._last_x: int | None = None
        self._last_y: int | None = None
        self._tk_img = None   # keep reference alive
        self._base_image: Image.Image | None = None
        self._resize_job = None
        self._scale: float = 1.0
        self._img_x: int = 0
        self._img_y: int = 0

    # ── Display ───────────────────────────────────────────────────────────────

    def show(self, pil_image: Image.Image) -> None:
        """Render a PIL Image onto the canvas."""
        self._base_image = pil_image
        self._redraw()

    def _on_resize(self, event: tk.Event) -> None:
        if self._resize_job is not None:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(50, self._redraw)

    def _redraw(self) -> None:
        if self._base_image is None:
            return
        
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw < 10 or ch < 10:
            return

        img_w, img_h = self._base_image.size
        self._scale = min(cw / img_w, ch / img_h)
        
        new_w = max(1, int(img_w * self._scale))
        new_h = max(1, int(img_h * self._scale))
        
        self._img_x = (cw - new_w) // 2
        self._img_y = (ch - new_h) // 2
        
        disp_img = self._base_image.resize((new_w, new_h), Image.Resampling.BILINEAR)
        self._tk_img = ImageTk.PhotoImage(disp_img)
        
        self.canvas.delete("all")
        self.canvas.create_image(self._img_x, self._img_y, anchor=tk.NW, image=self._tk_img)

    # ── Mouse event forwarding ────────────────────────────────────────────────

    def _get_real_coords(self, x: int, y: int) -> tuple[int, int]:
        if self._scale == 0:
            return x, y
        rx = (x - self._img_x) / self._scale
        ry = (y - self._img_y) / self._scale
        return int(rx), int(ry)

    def _press(self, event: tk.Event) -> None:
        self._last_x, self._last_y = event.x, event.y
        rx, ry = self._get_real_coords(event.x, event.y)
        self._on_press(rx, ry)

    def _drag(self, event: tk.Event) -> None:
        if self._last_x is not None:
            rx0, ry0 = self._get_real_coords(self._last_x, self._last_y)
            rx1, ry1 = self._get_real_coords(event.x, event.y)
            self._on_drag(rx0, ry0, rx1, ry1)
            self._last_x, self._last_y = event.x, event.y

    def _release(self, event: tk.Event) -> None:
        rx, ry = self._get_real_coords(event.x, event.y)
        self._on_release(rx, ry)
        self._last_x = self._last_y = None
