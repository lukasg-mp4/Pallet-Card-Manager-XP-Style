import tkinter as tk
from .colors import XP_BORDER_COLOR, XP_BEIGE, XP_BTN_BG
from .fonts import XP_FONT
from .title_bar import XPTitleBar

class XPInfoDialog(tk.Toplevel):
    def __init__(self, parent, title, message):
        super().__init__(parent)

        self.withdraw(); self.configure(bg=XP_BORDER_COLOR); self.overrideredirect(True)
        parent.update_idletasks(); w, h = 350, 150 

        try: x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (w // 2); y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (h // 2)
        except: x = (self.winfo_screenwidth() // 2) - (w // 2); y = (self.winfo_screenheight() // 2) - (h // 2)

        self.geometry(f"{w}x{h}+{x}+{y}")
        
        main_frame = tk.Frame(self, bg=XP_BORDER_COLOR, bd=3); main_frame.pack(fill=tk.BOTH, expand=True)
        self.title_bar = XPTitleBar(main_frame, self, app_instance=self, title_text=title, close_func=self.destroy)
        content = tk.Frame(main_frame, bg=XP_BEIGE, padx=20, pady=20); content.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(content, 
                 text=message, 
                 bg=XP_BEIGE, 
                 font=("Tahoma", 10), 
                 wraplength=300, 
                 justify="center").pack(pady=(5, 15), expand=True)
        
        btn_frame = tk.Frame(content, bg=XP_BEIGE); btn_frame.pack(side=tk.BOTTOM, fill=tk.X)

        tk.Button(btn_frame, 
                  text="OK", 
                  width=10, 
                  command=self.destroy, 
                  bg=XP_BTN_BG, 
                  relief="raised", 
                  bd=2, 
                  font=XP_FONT).pack(side=tk.BOTTOM)
        
        self.deiconify(); self.lift(); self.focus_force(); self.grab_set(); self.wait_window(self)

class XPErrorDialog(tk.Toplevel):
    def __init__(self, parent, title, message):
        super().__init__(parent)

        self.withdraw(); self.configure(bg=XP_BORDER_COLOR); self.overrideredirect(True)
        parent.update_idletasks(); w, h = 350, 160 

        try: x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (w // 2); y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (h // 2)
        except: x = (self.winfo_screenwidth() // 2) - (w // 2); y = (self.winfo_screenheight() // 2) - (h // 2)

        self.geometry(f"{w}x{h}+{x}+{y}")
        
        main_frame = tk.Frame(self, bg=XP_BORDER_COLOR, bd=3); main_frame.pack(fill=tk.BOTH, expand=True)
        self.title_bar = XPTitleBar(main_frame, self, app_instance=self, title_text=title, close_func=self.destroy)
        content = tk.Frame(main_frame, bg=XP_BEIGE, padx=20, pady=20); content.pack(fill=tk.BOTH, expand=True)
        
        icon_frame = tk.Frame(content, bg=XP_BEIGE); icon_frame.pack(side=tk.LEFT, anchor="n", pady=5)
        cvs = tk.Canvas(icon_frame, width=32, height=32, bg=XP_BEIGE, highlightthickness=0); cvs.pack()
        cvs.create_oval(2, 2, 30, 30, fill="red", outline="#8B0000")
        cvs.create_line(10, 10, 22, 22, fill="white", width=3); cvs.create_line(22, 10, 10, 22, fill="white", width=3)
        
        tk.Label(content, 
                 text=message, 
                 bg=XP_BEIGE, 
                 font=("Tahoma", 10), 
                 wraplength=240, 
                 justify="center").pack(side=tk.LEFT, padx=(15, 0), pady=5, expand=True)
        
        btn_frame = tk.Frame(content, bg=XP_BEIGE); btn_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        tk.Button(btn_frame, 
                  text="OK", 
                  width=10, 
                  command=self.destroy, 
                  bg=XP_BTN_BG, 
                  relief="raised", 
                  bd=2, 
                  font=XP_FONT).pack(side=tk.BOTTOM)
        
        self.deiconify(); self.lift(); self.focus_force(); self.grab_set(); self.wait_window(self)