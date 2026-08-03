from os import path
from tkinter import Tk
import locale
import platform

from classes.MainApp import MainApp

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

    # Configure Tkinter for Unicode support
    if platform.system() == 'Linux':
        default_font = ('Liberation Sans', 10)
    else:
        default_font = ('Arial', 10)

    root.option_add('*font', default_font)  # Set a readable default font with Cyrillic support
    root.tk.call('encoding', 'system', 'utf-8')  # Ensure UTF-8 encoding

    base_dir = path.dirname(path.abspath(__file__))
    app = MainApp(root, base_dir)
    root.mainloop()