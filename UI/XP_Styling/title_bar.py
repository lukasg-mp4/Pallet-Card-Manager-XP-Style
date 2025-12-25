import tkinter as tk
import sys
from .colors import XP_BORDER_COLOR
from .fonts import TITLE_FONT, BTN_FONT_CLOSE

class XPTitleBar(tk.Frame):
    def __init__(self, parent, root_window, app_instance=None, title_text="Application", close_func=None):
        super().__init__(parent, height=30, bg="#0058E6")
        self.root = root_window
        self.app = app_instance 
        self.close_func = close_func 
        self.pack(side=tk.TOP, fill=tk.X)
        self.pack_propagate(False) 
        
        self.canvas = tk.Canvas(self, bg="#0058E6", highlightthickness=0)
        self.canvas.place(relwidth=1, relheight=1)
        self.draw_gradient()
        
        self.canvas.create_text(11, 16, text=title_text, font=TITLE_FONT, fill="black", anchor="w") 
        self.canvas.create_text(10, 15, text=title_text, font=TITLE_FONT, fill="white", anchor="w") 

        self.btn_close = tk.Button(self,
                                   text="X",
                                   font=BTN_FONT_CLOSE,
                                   bg="#E7483C",
                                   fg="white",
                                   activebackground="#FF8A80",
                                   activeforeground="white",
                                   bd=1,
                                   relief="raised",
                                   command=self.close_app,
                                   width=3)
        
        self.btn_close.pack(side=tk.RIGHT, padx=3, pady=3)

        if self.app and hasattr(self.app, 'toggle_maximize'):

            self.btn_max = tk.Button(self,
                                     text="□",
                                     font=BTN_FONT_CLOSE,
                                     bg="#0054E3",
                                     fg="white",
                                     activebackground="#3A93EB",
                                     activeforeground="white",
                                     bd=1,
                                     relief="raised",
                                     command=self.app.toggle_maximize,
                                     width=3)
            
            self.btn_max.pack(side=tk.RIGHT, padx=1, pady=3)

            self.btn_min = tk.Button(self,
                                     text="_",
                                     font=BTN_FONT_CLOSE, 
                                     bg="#0054E3",
                                     fg="white",
                                     activebackground="#3A93EB",
                                     activeforeground="white",
                                     bd=1,
                                     relief="raised",
                                     command=self.app.minimize_app,
                                     width=3)
            
            self.btn_min.pack(side=tk.RIGHT, padx=1, pady=3)

        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.do_drag)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drag)

    def draw_gradient(self):
        c1 = (0, 88, 230); c2 = (58, 147, 235)

        for i in range(30):
            r = int(c1[0] + (c2[0] - c1[0]) * (i / 30))
            g = int(c1[1] + (c2[1] - c1[1]) * (i / 30))
            b = int(c1[2] + (c2[2] - c1[2]) * (i / 30))
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.canvas.create_line(0, i, 2000, i, fill=color, width=1)

    def start_drag(self, event):
        if self.app and hasattr(self.app, 'dragging'):
            self.app.dragging = True

            if hasattr(self.app, 'stop_timers'): self.app.stop_timers()

        self._offset_x = event.x
        self._offset_y = event.y

    def do_drag(self, event):
        if self.app and hasattr(self.app, 'maximized') and self.app.maximized:
            self.app.toggle_maximize(use_curtain=False)
            self.root.update_idletasks()
            curr_w = self.root.winfo_width()

            if curr_w < 100: curr_w = 1000
            self._offset_x = curr_w // 2
            self.root.deiconify()
            self.root.lift()

        x = event.x_root - self._offset_x
        y = event.y_root - self._offset_y
        if abs(x) > 10000 or abs(y) > 10000: x = 0; y = 0

        self.root.geometry(f"+{x}+{y}")

    def stop_drag(self, event):
        if self.app and hasattr(self.app, 'dragging'):
            self.app.dragging = False

            if hasattr(self.app, 'request_debounce_refresh'): self.app.request_debounce_refresh()

    def close_app(self):
        if self.close_func:
            self.close_func()
            
        else:
            self.root.destroy()
            sys.exit()