from os import path
import tkinter as tk

from classes.MainApp import MainApp

if __name__ == "__main__":
    root = tk.Tk()
    base_dir = path.dirname(path.abspath(__file__))
    app = MainApp(root, base_dir)
    root.mainloop()