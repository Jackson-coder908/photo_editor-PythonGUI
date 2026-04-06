"""
ui/status_bar.py
----------------
A simple one-line status bar pinned to the window bottom.
"""

import tkinter as tk


class StatusBar(tk.Label):
    def __init__(self, parent, **kwargs):
        self._var = tk.StringVar(value="Open an image to begin.")
        super().__init__(
            parent,
            textvariable=self._var,
            bg="#0d0d1a",
            fg="#a0a8c8",
            anchor=tk.W,
            padx=8,
            **kwargs,
        )

    def set(self, message: str) -> None:
        self._var.set(message)
