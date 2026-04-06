"""
ui/toolbar.py
-------------
Top toolbar: Open / Save / Clear / Undo buttons.
Communicates via callbacks — no direct dependency on the controller.
"""

import tkinter as tk


class Toolbar(tk.Frame):
    BTN = dict(fg="white", relief=tk.FLAT, padx=10, pady=4,
               cursor="hand2", activeforeground="white",
               bg="#0f3460", activebackground="#533483")

    def __init__(
        self,
        parent,
        on_open,
        on_save,
        on_clear,
        on_undo,
        **kwargs,
    ):
        super().__init__(parent, bg="#16213e", pady=6, **kwargs)
        tk.Button(self, text="📂  Open Image", command=on_open, **self.BTN).pack(side=tk.LEFT, padx=4)
        tk.Button(self, text="💾  Save",        command=on_save,  **self.BTN).pack(side=tk.LEFT, padx=4)
        tk.Button(self, text="🗑  Clear Drawing",command=on_clear, **self.BTN).pack(side=tk.LEFT, padx=4)
        tk.Button(self, text="↩  Undo",         command=on_undo,  **self.BTN).pack(side=tk.LEFT, padx=4)
