import tkinter as tk
from .colors import XP_BORDER_COLOR, XP_BEIGE, XP_BTN_BG
from .fonts import XP_FONT
from .title_bar import XPTitleBar

class XPMessageBox(tk.Toplevel):
    def __init__(self, parent, title, message):
        super().__init__(parent)

        self.result = False
        self.withdraw()
        self.configure(bg=XP_BORDER_COLOR)
        self.overrideredirect(True)
        
        parent.update_idletasks()
        w, h = 400, 200  

        try: x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (w // 2); y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (h // 2)
        except: x = (self.winfo_screenwidth() // 2) - (w // 2); y = (self.winfo_screenheight() // 2) - (h // 2)

        self.geometry(f"{w}x{h}+{x}+{y}")
        
        main_frame = tk.Frame(self, bg=XP_BORDER_COLOR, bd=3)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.title_bar = XPTitleBar(main_frame, self, title_text=title, close_func=self.cancel)

        content = tk.Frame(main_frame, bg=XP_BEIGE, padx=20, pady=20)
        content.pack(fill=tk.BOTH, expand=True)
        tk.Label(content, text=message, bg=XP_BEIGE, font=("Tahoma", 10), wraplength=350, justify="center").pack(expand=True, pady=(5, 20))

        btn_frame = tk.Frame(content, bg=XP_BEIGE)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        inner_btn_frame = tk.Frame(btn_frame, bg=XP_BEIGE)
        inner_btn_frame.pack(side=tk.BOTTOM)
        
        tk.Button(inner_btn_frame, 
                  text="Yes", 
                  width=10, 
                  command=self.confirm, 
                  bg=XP_BTN_BG, 
                  relief="raised", 
                  bd=2, font=XP_FONT).pack(side=tk.LEFT, padx=15)
        
        tk.Button(inner_btn_frame, 
                  text="No", 
                  width=10, 
                  command=self.cancel, 
                  bg=XP_BTN_BG, 
                  relief="raised", 
                  bd=2, font=XP_FONT).pack(side=tk.LEFT, padx=15)
        
        self.bind("<Return>", self.confirm)
        self.bind("<Escape>", self.cancel)
        self.deiconify(); self.lift(); self.focus_force(); self.grab_set(); self.wait_window(self)

    def confirm(self, event=None):
        self.result = True
        self.destroy()

    def cancel(self, event=None):
        self.result = False
        self.destroy()