import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont

from UI.XP_Styling.colors import XP_BORDER_COLOR, XP_BEIGE, XP_BTN_BG
from UI.XP_Styling.fonts import XP_FONT, XP_FONT_BOLD
from UI.XP_Styling.title_bar import XPTitleBar
from UI.XP_Styling.notifications import XPInfoDialog
from Print_Manager.system import get_system_printers, get_default_printer

class PrintDialog(tk.Toplevel):
    def __init__(self, parent, app_manager, initial_sheet_name):
        super().__init__(parent)
        self.withdraw()
        self.overrideredirect(True)
        self.configure(bg=XP_BORDER_COLOR)
        
        self.app = app_manager
        self.current_sheet_name = initial_sheet_name
        self.data = []; self.current_index = 0
        self.a_key_held = False; self.updating_nav = False
        self.canvas_ready = False 

        self.printers = get_system_printers()
        self.selected_printer = tk.StringVar(value=get_default_printer())

        if self.selected_printer.get() == "" and self.printers:
            self.selected_printer.set(self.printers[0])

        w, h = 700, 500

        try: x = parent.winfo_rootx() + (parent.winfo_width()//2) - (w//2); y = parent.winfo_rooty() + (parent.winfo_height()//2) - (h//2)
        except: x = 0; y = 0

        self.geometry(f"{w}x{h}+{x}+{y}")

        self.setup_ui()
        self.load_data()
        
        self.bind("<KeyPress-a>", lambda e: setattr(self, 'a_key_held', True))
        self.bind("<KeyRelease-a>", lambda e: setattr(self, 'a_key_held', False))
        self.bind("<Return>", self.handle_enter)
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<Left>", lambda e: self.go_prev())
        self.bind("<Right>", lambda e: self.go_next())
        
        self.deiconify(); self.focus_force(); self.grab_set()

    def setup_ui(self):
        main = tk.Frame(self, bg=XP_BORDER_COLOR, bd=3); main.pack(fill=tk.BOTH, expand=True)
        self.title_bar = XPTitleBar(main, self, title_text="Print Inventory Labels", close_func=self.destroy)
        content = tk.Frame(main, bg=XP_BEIGE); content.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(content, bg="#404040", width=320, relief="sunken", bd=2)
        left.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10); left.pack_propagate(False)
        tk.Label(left, text="PREVIEW", font=("Tahoma", 10, "bold"), bg="#303030", fg="white", pady=5).pack(fill=tk.X)
        self.preview_canvas = tk.Canvas(left, bg="#404040", highlightthickness=0)
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        
        self.preview_canvas.bind("<Configure>", self.on_canvas_resize)

        right = tk.Frame(content, bg=XP_BEIGE, padx=10, pady=10); right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tk.Label(right, text="Select Sheet:", font=("Tahoma", 10, "bold"), bg=XP_BEIGE).pack(anchor="w")
        self.sheet_combo = ttk.Combobox(right, values=list(self.app.sheets.keys()), state="readonly")
        self.sheet_combo.set(self.current_sheet_name)
        self.sheet_combo.pack(fill=tk.X, pady=(5, 10))
        self.sheet_combo.bind("<<ComboboxSelected>>", self.on_sheet_change)

        tk.Label(right, text="Select Printer:", font=("Tahoma", 10, "bold"), bg=XP_BEIGE).pack(anchor="w")
        ttk.Combobox(right, textvariable=self.selected_printer, values=self.printers, state="readonly").pack(fill=tk.X, pady=(5, 10))

        self.lbl_counter = tk.Label(right, text="", font=("Tahoma", 12, "bold"), bg=XP_BEIGE, fg="blue")
        self.lbl_counter.pack(anchor="w", pady=(5, 0))
        qty_frame = tk.Frame(right, bg=XP_BEIGE); qty_frame.pack(fill=tk.X, pady=2)
        tk.Label(qty_frame, text="Quantity to Print:", font=("Tahoma", 10), bg=XP_BEIGE).pack(side=tk.LEFT)
        self.lbl_copies = tk.Label(qty_frame, text="", font=("Tahoma", 11, "bold"), bg=XP_BEIGE, fg="red")
        self.lbl_copies.pack(side=tk.LEFT, padx=5)

        nav = tk.Frame(right, bg=XP_BEIGE); nav.pack(fill=tk.X, pady=(15, 5))
        self.btn_prev = tk.Button(nav, text="< Prev", command=self.go_prev, bg=XP_BTN_BG, relief="raised", bd=2, font=XP_FONT, width=9); self.btn_prev.pack(side=tk.LEFT)
        self.nav_var = tk.StringVar(); self.nav_var.trace("w", self.on_nav_change)
        tk.Entry(nav, textvariable=self.nav_var, font=("Tahoma", 10), justify="center", relief="sunken", bd=2).pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)
        self.btn_next = tk.Button(nav, text="Next >", command=self.go_next, bg=XP_BTN_BG, relief="raised", bd=2, font=XP_FONT, width=9); self.btn_next.pack(side=tk.RIGHT)

        instr = tk.LabelFrame(right, text="Shortcuts", bg=XP_BEIGE, font=("Tahoma", 8, "bold"))
        instr.pack(fill=tk.X, pady=10, ipadx=5, ipady=5)

        for t in ["[Left/Right]: Navigate", "[Enter]: Print Current", "[Hold 'A' + Enter]: Print ALL", "[Esc]: Close"]:
            tk.Label(instr, text=t, bg=XP_BEIGE, font=XP_FONT, anchor="w").pack(fill=tk.X)

        btn_box = tk.Frame(right, bg=XP_BEIGE); btn_box.pack(side=tk.BOTTOM, fill=tk.X)
        self.btn_p_curr = tk.Button(btn_box, text="Print Current", command=self.print_current, bg=XP_BTN_BG, relief="raised", bd=2, font=XP_FONT_BOLD, height=2); self.btn_p_curr.pack(fill=tk.X, pady=5)
        self.btn_p_all = tk.Button(btn_box, text="Print ALL", command=self.print_all, bg="#d9ffd9", relief="raised", bd=2, font=XP_FONT_BOLD, height=2); self.btn_p_all.pack(fill=tk.X, pady=5)

    def on_canvas_resize(self, event):
        self.canvas_ready = True
        self.update_view(skip_input=True)

    def load_data(self):
        if self.current_sheet_name in self.app.sheets:
            self.data = self.app.sheets[self.current_sheet_name].get_completed_rows()
            self.current_index = 0
            self.update_view()

        else: self.data = []; self.update_view()

    def update_view(self, skip_input=False):
        if not self.data:
            self.lbl_counter.config(text="No completed docs"); self.lbl_copies.config(text="")
            self.preview_canvas.delete("all")

            for b in [self.btn_p_curr, self.btn_p_all, self.btn_prev, self.btn_next]: b.config(state="disabled")

            if not skip_input: self.updating_nav = True; self.nav_var.set(""); self.updating_nav = False

            return

        for b in [self.btn_p_curr, self.btn_p_all]: b.config(state="normal")

        item = self.data[self.current_index]
        self.lbl_counter.config(text=f"Document {self.current_index + 1} of {len(self.data)}")
        self.lbl_copies.config(text=f"{item['copies']} Labels")
        self.btn_prev.config(state="disabled" if self.current_index == 0 else "normal")
        self.btn_next.config(state="disabled" if self.current_index == len(self.data) - 1 else "normal")

        if not skip_input: self.updating_nav = True; self.nav_var.set(str(self.current_index + 1)); self.updating_nav = False
        
        if self.canvas_ready:
            self.draw_preview(item)

    def draw_preview(self, item):
        self.preview_canvas.delete("all")
        cw = self.preview_canvas.winfo_width()
        ch = self.preview_canvas.winfo_height()
        
        if cw <= 1: cw = 320
        if ch <= 1: ch = 380
        
        w, h = 240, 340
        x1 = (cw - w) // 2
        y1 = (ch - h) // 2
        
        self.preview_canvas.create_rectangle(x1, y1, x1+w, y1+h, fill="#eaffea", outline="black", width=1)
        
        def get_font(text, max_w, start_s):
            s = start_s; f = tkfont.Font(family="Tahoma", size=s, weight="bold")

            while f.measure(text) > max_w and s > 10: s -= 2; f.configure(size=s)
            return ("Tahoma", s, "bold")

        mx = w * 0.9
        f1 = get_font(item['larousse'], mx, int(w*0.28))
        self.preview_canvas.create_text(x1+w/2, y1+(h*0.2), text=item['larousse'], font=f1)

        f2 = get_font(item['bbd'], mx, int(w*0.26))
        self.preview_canvas.create_text(x1+w/2, y1+(h*0.5), text=item['bbd'], font=f2)

        f3 = get_font(f"X {item['qty']}", mx, int(w*0.28))
        self.preview_canvas.create_text(x1+w/2, y1+(h*0.8), text=f"X {item['qty']}", font=f3)

    def on_sheet_change(self, event): self.current_sheet_name = self.sheet_combo.get(); self.load_data()

    def on_nav_change(self, *args):
        if self.updating_nav: return

        val = self.nav_var.get()
        if val.isdigit():
            idx = int(val) - 1
            if 0 <= idx < len(self.data): self.current_index = idx; self.update_view(skip_input=True)

    def go_prev(self): 
        if self.current_index > 0: self.current_index -= 1; self.update_view()

    def go_next(self): 
        if self.current_index < len(self.data) - 1: self.current_index += 1; self.update_view()

    def handle_enter(self, event): self.print_all() if self.a_key_held else self.print_current()

    def print_current(self):
        if not self.data: return
        
        self.app.start_print_job(self.current_sheet_name, [self.data[self.current_index]])
        self.destroy(); XPInfoDialog(self.app.root, "Queued", "Print job queued.")

    def print_all(self):
        if not self.data: return

        self.app.start_print_job(self.current_sheet_name, self.data[self.current_index:])
        self.destroy(); XPInfoDialog(self.app.root, "Queued", "All items queued.")