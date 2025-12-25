import tkinter as tk
from .colors import XP_BORDER_COLOR

class Resizer:
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.resize_mode = None
        self.start_x = 0; self.start_y = 0
        self.start_geo = None
        self.t = 5 
        bg_col = XP_BORDER_COLOR 
        
        self.cursors = {
            'n': 'size_ns', 's': 'size_ns', 'w': 'size_we', 'e': 'size_we',
            'nw': 'size_nw_se', 'ne': 'size_ne_sw', 'sw': 'size_ne_sw', 'se': 'size_nw_se'
        }

        self.sides = {
            'n':  (0, 0, 1.0, None, 'nw'), 's':  (0, 1.0, 1.0, None, 'sw'),
            'w':  (0, 0, None, 1.0, 'nw'), 'e':  (1.0, 0, None, 1.0, 'ne'),
        }
        
        for side, (rx, ry, rw, rh, anc) in self.sides.items():
            f = tk.Frame(self.root, bg=bg_col, cursor=self.cursors[side])

            if side in ['n', 's']: f.place(relx=rx, rely=ry, relwidth=rw, height=self.t, anchor=anc)
            else: f.place(relx=rx, rely=ry, relheight=rh, width=self.t, anchor=anc)

            self.bind_events(f, side)
            f.lift() 

        ct = 10 
        for corner in ['nw', 'ne', 'sw', 'se']:
            f = tk.Frame(self.root, bg=bg_col, cursor=self.cursors[corner])
            fx = 0 if 'w' in corner else 1.0
            fy = 0 if 'n' in corner else 1.0
            f.place(relx=fx, rely=fy, width=ct, height=ct, anchor=corner)
            self.bind_events(f, corner)
            f.lift()

    def bind_events(self, widget, mode):
        widget.bind("<ButtonPress-1>", lambda e: self.start_resize(e, mode))
        widget.bind("<B1-Motion>", self.do_resize)
        widget.bind("<ButtonRelease-1>", self.stop_resize)

    def start_resize(self, event, mode):
        if self.app.maximized: return 

        self.resize_mode = mode
        self.start_x = event.x_root
        self.start_y = event.y_root
        x = self.root.winfo_x(); y = self.root.winfo_y()
        w = self.root.winfo_width(); h = self.root.winfo_height()
        self.start_geo = (x, y, w, h)

    def do_resize(self, event):
        if not self.start_geo: return

        dx = event.x_root - self.start_x; dy = event.y_root - self.start_y
        x, y, w, h = self.start_geo
        new_w = w; new_h = h; new_x = x; new_y = y
        mode = self.resize_mode; min_w = 500; min_h = 400
        
        if 'e' in mode: new_w = max(min_w, w + dx)

        elif 'w' in mode:
            proposed_w = w - dx
            if proposed_w >= min_w: new_w = proposed_w; new_x = x + dx

            else: new_w = min_w; new_x = x + (w - min_w)

        if 's' in mode: new_h = max(min_h, h + dy)

        elif 'n' in mode:
            proposed_h = h - dy
            if proposed_h >= min_h: new_h = proposed_h; new_y = y + dy

            else: new_h = min_h; new_y = y + (h - min_h)
            
        self.root.geometry(f"{new_w}x{new_h}+{new_x}+{new_y}")

    def stop_resize(self, event):
        self.start_geo = None