import tkinter as tk
from tkinter import ttk
from info import PayoutInfo
from .edit_frame import EditWindow


class AcademyFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.tree = self.create_tree()
        self.tree.pack(padx=10, pady=10)

        edit_button = ttk.Button(self, text='edit')
        edit_button.pack(padx=10, pady=10)

        def open_edit_window():
            window = EditWindow(self)
            window.bind_func(self.load_payout)

        edit_button.bind('<Button-1>', lambda e: open_edit_window())

    def create_tree(self) -> ttk.Treeview:
        academy = PayoutInfo().academy

        columns = tuple(academy._asdict().keys())
        print(columns)
        column_widths = (100, 150, 150)
        tree = ttk.Treeview(self, columns=columns, show='headings')

        for key, width in zip(columns, column_widths):
            tree.column(key, width=width)
            tree.heading(key, text=key)

        tree.insert("", "end", "academy", values=academy)

        return tree

    def load_payout(self):
        academy = PayoutInfo().academy
        self.tree.item("academy", value=academy)
        print('load')
