"""
main.py
-------
Application entry point.  Run with:  python main.py
"""

import tkinter as tk
from photo_editor.controller import PhotoEditorApp

if __name__ == "__main__":
    root = tk.Tk()
    PhotoEditorApp(root)
    root.mainloop()
