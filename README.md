# 🎨 Python RGB Master Editor

---

## 🚀 Features

* ✏️ **Pen Tool** – Draw smooth strokes on the image
* ⬜ **Eraser Tool** – Remove drawn content
* 🅰️ **Text Tool** – Add text anywhere on the image
* ↖ **Move Text Tool** – Drag and reposition text
* 🎚 **Filters** – Adjust blur, contrast, grayscale
* 🔄 **Undo System** – Revert changes easily
* 🧼 **Clear Canvas** – Reset drawings instantly

---

## 🧠 How It Works

The editor uses a **two-layer system**:

* **Stroke Layer** → Stores pen & eraser drawings
* **Text Metadata** → Stores text separately

👉 Final image is rebuilt every frame using a processing pipeline
👉 This prevents bugs like ghost text and keeps editing clean

---

## 📂 Project Structure

```
photo_editor/
│
├── core/          # Image state & processing
├── tools/         # Pen, eraser, text, move tools
├── ui/            # Toolbar, canvas, panels
└── controller.py  # Main app controller
```

---

## ▶️ How to Run

1. Install dependencies:

```
pip install pillow
```

2. Run the app:

```
python controller.py
```

---

## 📸 Usage

1. Click **Open** to load an image
2. Select a tool from the side panel
3. Draw, erase, or add text
4. Apply filters
5. Save your edited image

---

## 🛠 Tech Stack

* Python 🐍
* Tkinter (GUI)
* Pillow (Image Processing)

---

## 📌 Future Improvements

* Brush smoothing / pressure support
* Layers panel
* Crop & resize tools
* Keyboard shortcuts

---

## 🙌 Credits

Built as a learning project to understand:

* image processing
* GUI design
* tool architecture

---

## ⭐ Show Support

If you like this project, give it a ⭐ on GitHub!
