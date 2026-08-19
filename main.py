from os import path
import locale
from PIL import Image, ImageTk
#from tkinter import font
from tkinterdnd2 import Tk

from classes.MainApp import MainApp
from Helpers import Helpers

# Load preferences

if __name__ == "__main__":
    # Set locale to support Cyrillic input
    try:
        locale.setlocale(locale.LC_ALL, '')
    except locale.Error:
        # Fallback to UTF-8 locale if system default fails
        try:
            locale.setlocale(locale.LC_ALL, 'C.UTF-8')
        except locale.Error:
            pass  # Use system default

    root = Tk()
    base_dir = path.dirname(path.abspath(__file__))
    preferences_path = path.join(base_dir, "settings", "preferences.json")
    icon_image = Image.open(path.join(base_dir, "icon.ico"))
    icon = ImageTk.PhotoImage(icon_image, master=root)
    root.iconphoto(True, icon)

    # Configure Tkinter for Unicode support
    root.tk.call('encoding', 'system', 'utf-8')  # Ensure UTF-8 encoding

    default_font = Helpers.get_ui_font(preferences_file_path=preferences_path, size_key="body_size")

    app = MainApp(root, base_dir, default_font)
    root.mainloop()