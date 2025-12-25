import tkinter as tk
import tkinter.font as tkfont
from UI.XP_Styling.fonts import XP_FONT_BOLD

class PreviewPane(tk.Frame):
    def __init__(self, parent, app_manager, width=780):
        super().__init__(parent, width=width, bg="#404040", relief="sunken", bd=2)
        self.app = app_manager
        self.pack_propagate(False)
        self.font_cache = {}
        self.measure_font = tkfont.Font(family="Tahoma", size=10, weight="bold")
        
        self.cached_data = []
        self.view_index = 0
        self.last_canvas_width = 0

        self.setup_ui()

    def setup_ui(self):
        tk.Label(self, text="COMPLETED DOCUMENTS", font=("Tahoma", 14, "bold"), bg="#303030", fg="white", pady=10).pack(fill=tk.X)
        self.canvas = tk.Canvas(self, bg="#404040", highlightthickness=0)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self.on_resize)
        
        # --- FIX: Restore MouseWheel Binding ---
        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", self.on_mousewheel))
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))

        # Navigation Bar
        nav = tk.Frame(self, bg="#303030", height=40)
        nav.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Buttons now call the Utils directly via App
        tk.Button(nav, text="<", font=XP_FONT_BOLD, command=lambda: self.app.preview_scroller.prev_doc(), width=4).pack(side=tk.LEFT, padx=10, pady=5)
        
        self.lbl_status = tk.Label(nav, text="No Documents", font=("Tahoma", 10), bg="#303030", fg="white")
        self.lbl_status.pack(side=tk.LEFT, expand=True)
        
        tk.Button(nav, text=">", font=XP_FONT_BOLD, command=lambda: self.app.preview_scroller.next_doc(), width=4).pack(side=tk.RIGHT, padx=10, pady=5)

    def refresh(self, data, active_row_index=None):
        self.cached_data = data
        self.view_index = -1
        if active_row_index is not None:
            for i, item in enumerate(self.cached_data):
                if item['row_idx'] == active_row_index:
                    self.view_index = i
                    break
        self.redraw()

    # --- FIX: MouseWheel Handler ---
    def on_mousewheel(self, event):
        if event.delta < 0:
            self.app.preview_scroller.next_doc()
        else:
            self.app.preview_scroller.prev_doc()

    def redraw(self):
        self.canvas.delete("all")
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        
        if not self.cached_data or self.view_index == -1:
            msg = "No completed rows" if not self.cached_data else "Row Incomplete"
            self.lbl_status.config(text=msg)
            self.canvas.create_text(w//2, h//2, text=msg, font=("Tahoma", 14), fill="#888888")
            return

        self.lbl_status.config(text=f"Document {self.view_index + 1} of {len(self.cached_data)}")
        item = self.cached_data[self.view_index]
        
        target_h = h - 60
        aspect = 520 / 735 
        target_w = int(target_h * aspect)
        if target_w > (w - 60): target_w = w - 60; target_h = int(target_w / aspect)
        
        x_pad, y_pos = (w - target_w) // 2, (h - target_h) // 2
        
        self.canvas.create_rectangle(x_pad, y_pos, x_pad+target_w, y_pos+target_h, fill="#eaffea", outline="black", width=1)
        self.draw_content(item, x_pad, y_pos, target_w, target_h)

    def draw_content(self, values, x, y, w, h):
        cx = x + (w // 2)
        max_txt = w * 0.9
        def draw_line(text, y_pct, size_pct):
            size = int(w * size_pct)
            font = self.get_fitting_font(text, max_txt, size)
            self.canvas.create_text(cx, y + (h * y_pct), text=text, font=font, fill="black")

        draw_line(values['larousse'], 0.20, 0.28)
        draw_line(values['bbd'], 0.50, 0.26)
        draw_line(f"X {values['qty']}", 0.80, 0.28)

    def get_fitting_font(self, text, max_width, start_size):
        key = (text, int(max_width), start_size)
        if key in self.font_cache: return self.font_cache[key]
        size = start_size
        self.measure_font.configure(size=size)
        while self.measure_font.measure(text) > max_width and size > 20:
            size -= 5
            self.measure_font.configure(size=size)
        res = ("Tahoma", size, "bold")
        self.font_cache[key] = res
        return res

    def on_resize(self, event):
        if abs(event.width - self.last_canvas_width) > 2:
            self.last_canvas_width = event.width
            self.redraw()