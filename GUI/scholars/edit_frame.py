import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable
from info import PayoutInfo


class InputFrame(tk.Frame):
    def __init__(self, master, scholar_index: int):
        super().__init__(master)

        scholar = PayoutInfo().scholar_list[scholar_index]
        self.scholar_var_dict = {key: tk.StringVar(self, value=value)
                                 for key, value in scholar._asdict().items()}

        for key in self.scholar_var_dict.keys():
            frame = tk.Frame(self)

            ttk.Label(frame, text=key, width=30,
                      ).pack(side=tk.LEFT)

            academy_var = self.scholar_var_dict[key]
            tk.Entry(frame, width=30,
                     textvariable=academy_var).pack(side=tk.LEFT)
            frame.pack()

    def to_info_dict(self):
        return {key: self.scholar_var_dict[key].get()
                for key in self.scholar_var_dict.keys()}


class ControlFrame(tk.Frame):
    def __init__(self, master, scholar_index: int):
        super().__init__(master)

        self.save_button = ttk.Button(self, text='save')
        self.save_button.pack(side=tk.LEFT)

        self.cancel_button = ttk.Button(self, text='cancel')
        self.cancel_button.pack(side=tk.LEFT)

        self.scholar_index = scholar_index

    def bind_cancel(self, master_window: tk.Toplevel):
        self.cancel_button.bind(
            '<Button-1>', lambda x: master_window.destroy())

    def bind_save(self, info_dict_func: Callable[[], dict],
                  load_payout_func: Callable[[], None]):
        def save():
            if info_dict_func is None:
                raise ValueError('info_dict_func is NOT set')

            if not messagebox.askokcancel('save', 'save ?'):
                return

            scholar_dict = info_dict_func()
            PayoutInfo().rewrite_scholar(scholar_dict, self.scholar_index)

            load_payout_func()

        self.save_button.bind('<Button-1>', lambda x: save())


class EditWindow(tk.Toplevel):
    def __init__(self, master, scholar_index: int):
        super().__init__(master, name='edit')
        self.grab_set()

        self.input_frame = InputFrame(self, scholar_index)
        self.input_frame.pack(padx=20, pady=20)

        self.control_frame = ControlFrame(self, scholar_index)
        self.control_frame.pack(padx=20, pady=20)

    def bind_func(self, load_payout_func: Callable[[], None]):
        self.control_frame.bind_save(self.input_frame.to_info_dict,
                                     load_payout_func)
        self.control_frame.bind_cancel(self)
