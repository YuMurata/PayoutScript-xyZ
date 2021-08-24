import tkinter as tk
from tkinter import ttk
from academy.academy_frame import AcademyFrame
from scholars.scholars_frame import ScholarsFrame


class MainFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        note = ttk.Notebook(self)

        academy_frame = AcademyFrame(note)
        note.add(academy_frame, text='Academy')

        scholar_frame = ScholarsFrame(note)
        note.add(scholar_frame, text='Scholars')

        note.pack()


if __name__ == "__main__":
    root = tk.Tk()
    MainFrame(root).pack()
    root.mainloop()
