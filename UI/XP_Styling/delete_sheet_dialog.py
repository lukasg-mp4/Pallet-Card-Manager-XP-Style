import tkinter as tk
import tkinter.ttk as ttk
from .colors import XP_BORDER_COLOR, XP_BEIGE, XP_BTN_BG
from .fonts import XP_FONT
from .title_bar import XPTitleBar

class XPDeleteSheetDialog(tk.Toplevel):
    def __init__(self, parent, sheet_list, current_selection):
        super().__init__(parent)
        self.result = None
        
        self.withdraw()
        self.configure(bg=XP_BORDER_COLOR)
        self.overrideredirect(True)
        
        parent.update_idletasks()
        w, h = 350, 180 

        try: 
            x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (w // 2)
            y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (h // 2)

        except: 
            x = (self.winfo_screenwidth() // 2) - (w // 2)
            y = (self.winfo_screenheight() // 2) - (h // 2)

        self.geometry(f"{w}x{h}+{x}+{y}")
        
        main_frame = tk.Frame(self, bg=XP_BORDER_COLOR, bd=3)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.title_bar = XPTitleBar(main_frame, 
                                    self, 
                                    app_instance=self, 
                                    title_text="Delete Sheet", 
                                    close_func=self.cancel)
        
        content = tk.Frame(main_frame, bg=XP_BEIGE, padx=20, pady=20)
        content.pack(fill=tk.BOTH, expand=True)
        tk.Label(content, text="Select the sheet you want to delete:", bg=XP_BEIGE, font=("Tahoma", 9)).pack(anchor="w", pady=(0, 5))
        
        self.combo_var = tk.StringVar(value=current_selection)
        self.combo = ttk.Combobox(content, 
                                  textvariable=self.combo_var, 
                                  values=sheet_list, 
                                  state="readonly", 
                                  font=("Tahoma", 9))
        self.combo.pack(fill=tk.X, pady=5)
        
        btn_frame = tk.Frame(content, bg=XP_BEIGE)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))
        tk.Button(btn_frame, 
                  text="OK", 
                  width=10, 
                  command=self.ok, 
                  bg=XP_BTN_BG, 
                  relief="raised",
                  bd=2, 
                  font=XP_FONT).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(btn_frame, 
                  text="Cancel", 
                  width=10, 
                  command=self.cancel, 
                  bg=XP_BTN_BG, 
                  relief="raised", 
                  bd=2, 
                  font=XP_FONT).pack(side=tk.RIGHT, padx=5)
        
        self.bind("<Escape>", self.cancel)
        self.bind("<Return>", self.ok)
        
        self.deiconify()
        self.lift()
        self.grab_set()
        self.wait_window(self)

    def ok(self, event=None):
        self.result = self.combo_var.get()
        self.destroy()

    def cancel(self, event=None):
        self.result = None
        self.destroy()