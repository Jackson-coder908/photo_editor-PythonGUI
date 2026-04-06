"""
ui/side_panel.py
----------------
Right-hand control panel: image adjustments, drawing tools, colour picker,
pen size, text options.  Exposes only plain Python properties / callbacks.
"""

import tkinter as tk
from tkinter import colorchooser


class SidePanel(tk.Frame):
    _SECTION_CFG = dict(bg="#16213e", fg="#a0a8c8", font=("Courier", 9, "bold"))
    _LABEL_CFG   = dict(bg="#16213e", fg="white")
    _SCALE_CFG   = dict(orient=tk.HORIZONTAL, length=200, bg="#16213e",
                        fg="white", troughcolor="#0f3460", highlightthickness=0)
    _BTN_CFG     = dict(relief=tk.FLAT, padx=8, pady=4, cursor="hand2",
                        bg="#0f3460", fg="white",
                        activebackground="#533483", activeforeground="white")
    _TOOL_CFG    = dict(relief=tk.FLAT, padx=8, pady=4, cursor="hand2", width=8)

    def __init__(self, parent, on_tool_change, on_filter_change, **kwargs):
        super().__init__(parent, bg="#16213e", width=220, **kwargs)
        self.pack_propagate(False)

        self._on_tool_change   = on_tool_change
        self._on_filter_change = on_filter_change

        self.pen_color  = "#ff4444"
        self._tool_btns: dict[str, tk.Button] = {}

        self._build()

    # ── Public properties (read by the controller) ────────────────────────────

    @property
    def contrast(self) -> float:
        return float(self._contrast.get())

    @property
    def grayscale(self) -> float:
        return self._grayscale.get() / 100.0

    @property
    def blur(self) -> int:
        return int(self._blur.get())

    @property
    def pen_size(self) -> int:
        return self._pen_size.get()

    @property
    def font_size(self) -> int:
        return self._font_size.get()

    @property
    def bold(self) -> bool:
        return self._bold.get()

    # ── Tool button highlight ─────────────────────────────────────────────────

    def highlight_tool(self, active: str) -> None:
        for name, btn in self._tool_btns.items():
            btn.config(bg="#533483" if name == active else "#0f3460")

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build(self) -> None:
        self._section("── IMAGE ADJUSTMENTS ──")
        self._contrast  = self._slider("Contrast",   0.5, 3.0, 1.0, resolution=0.1)
        self._grayscale = self._slider("Grayscale %", 0,  100,  0)
        self._blur      = self._slider("Blur Radius",  0,    5,  0)

        self._section("── DRAWING TOOLS ──")
        self._build_tool_buttons()

        self._section("── PEN COLOR ──")
        self._build_color_picker()

        self._section("── PEN SIZE ──")
        self._pen_size = tk.IntVar(value=3)
        tk.Scale(self, variable=self._pen_size, from_=1, to=30,
                 **self._SCALE_CFG).pack(padx=8)

        self._section("── TEXT OPTIONS ──")
        self._font_size = tk.IntVar(value=24)
        tk.Label(self, text="Font size", **self._LABEL_CFG).pack(anchor=tk.W, padx=10)
        tk.Scale(self, variable=self._font_size, from_=8, to=120,
                 **self._SCALE_CFG).pack(padx=8)
        self._bold = tk.BooleanVar(value=False)
        tk.Checkbutton(self, text="Bold", variable=self._bold,
                       bg="#16213e", fg="white", selectcolor="#0f3460",
                       activebackground="#16213e",
                       activeforeground="white").pack(anchor=tk.W, padx=10)

    def _section(self, text: str) -> None:
        tk.Label(self, text=text, **self._SECTION_CFG).pack(
            anchor=tk.W, padx=8, pady=(10, 2))

    def _slider(self, label: str, lo, hi, default, resolution=1) -> tk.Scale:
        tk.Label(self, text=label, **self._LABEL_CFG).pack(anchor=tk.W, padx=10)
        s = tk.Scale(self, from_=lo, to=hi, resolution=resolution,
                     command=lambda _: self._on_filter_change(),
                     **self._SCALE_CFG)
        s.set(default)
        s.pack(padx=8)
        return s

    def _build_tool_buttons(self) -> None:
        frame = tk.Frame(self, bg="#16213e")
        frame.pack(fill=tk.X, padx=8, pady=4)

        tools = [
            ("pen",       "✏ Pen",      0, 0),
            ("eraser",    "⬜ Erase",    0, 1),
            ("text",      "T  Text",    1, 0),
            ("move_text", "↖ Move Text",1, 1),
            ("none",      "🚫 None",    2, 0),
        ]
        for name, label, row, col in tools:
            btn = tk.Button(
                frame, text=label,
                command=lambda n=name: self._on_tool_change(n),
                **self._TOOL_CFG,
                bg="#533483" if name == "none" else "#0f3460",
                fg="white",
                activebackground="#533483", activeforeground="white",
            )
            btn.grid(row=row, column=col, padx=2, pady=2)
            self._tool_btns[name] = btn

    def _build_color_picker(self) -> None:
        self._color_preview = tk.Canvas(
            self, width=50, height=24, bg=self.pen_color,
            highlightthickness=1, highlightbackground="#533483", cursor="hand2")
        self._color_preview.pack(anchor=tk.W, padx=10, pady=2)
        self._color_preview.bind("<Button-1>", lambda e: self._pick_color())
        tk.Button(self, text="Choose Color…", command=self._pick_color,
                  **self._BTN_CFG).pack(padx=10, pady=2, anchor=tk.W)

    def _pick_color(self) -> None:
        result = colorchooser.askcolor(color=self.pen_color, title="Choose Draw Color")
        if result[1]:
            self.pen_color = result[1]
            self._color_preview.config(bg=self.pen_color)
