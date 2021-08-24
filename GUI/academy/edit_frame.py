import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable
from info import PayoutInfo


class InputFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        academy_info = PayoutInfo().academy_info
        self.academy_var_dict = {key: tk.StringVar(self)
                                 for key in academy_info._asdict().keys()}

        self.load_payout()

        for key in self.academy_var_dict.keys():
            frame = tk.Frame(self)

            ttk.Label(frame, text=key, width=20,
                      ).pack(side=tk.LEFT)

            academy_var = self.academy_var_dict[key]
            tk.Entry(frame, width=30,
                     textvariable=academy_var).pack(side=tk.LEFT)
            frame.pack()

    def to_info_dict(self):
        return {key: self.academy_var_dict[key].get()
                for key in self.academy_var_dict.keys()}

    def load_payout(self):
        academy_info = PayoutInfo().academy_info

        for key, value in academy_info._asdict().items():
            self.academy_var_dict[key].set(value)


class ControlFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.save_button = ttk.Button(self, text='save')
        self.save_button.pack(side=tk.LEFT)

        self.cancel_button = ttk.Button(self, text='cancel')
        self.cancel_button.pack(side=tk.LEFT)

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

            academy_dict = info_dict_func()
            PayoutInfo().rewrite_academy(academy_dict)

            load_payout_func()

        self.save_button.bind('<Button-1>', lambda x: save())


class EditWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master, name='edit')
        self.grab_set()

        self.input_frame = InputFrame(self)
        self.input_frame.pack(padx=20, pady=20)

        self.control_frame = ControlFrame(self)
        self.control_frame.pack(padx=20, pady=20)

    def bind_func(self, load_payout_func: Callable[[], None]):
        self.control_frame.bind_save(self.input_frame.to_info_dict,
                                     load_payout_func)
        self.control_frame.bind_cancel(self)
