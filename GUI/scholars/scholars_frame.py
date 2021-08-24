import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from typing import Tuple
from info import PayoutInfo, ScholarInfo
from .edit_frame import EditWindow


class ScholarsFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.tree = self.create_tree()
        self.tree.pack(padx=10, pady=10)

        self.item_id_list: Tuple[str] = tuple([])
        self.load_payout()

        edit_button = ttk.Button(self, text='edit')
        edit_button.pack(padx=10, pady=10)

        def open_edit_window():
            selection_list = self.tree.selection()
            if len(selection_list) < 1:
                messagebox.showerror('error', 'select scholar')
                return

            scholar_index = int(selection_list[0])
            window = EditWindow(self, scholar_index)
            window.bind_func(self.load_payout)

        edit_button.bind('<Button-1>', lambda e: open_edit_window())

    def create_tree(self) -> ttk.Treeview:
        columns = tuple(ScholarInfo._fields)
        print(columns)
        column_widths = (100, 150, 150, 150, 150)
        tree = ttk.Treeview(self, columns=columns, show='headings')

        for key, width in zip(columns, column_widths):
            tree.column(key, width=width)
            tree.heading(key, text=key)

        return tree

    def load_payout(self):
        for item_id in self.item_id_list:
            self.tree.delete(item_id)

        scholar_list = PayoutInfo().scholar_list
        self.item_id_list = tuple([self.tree.insert("", "end", iid=i,
                                                    values=scholar)
                                   for i, scholar in enumerate(scholar_list)])
