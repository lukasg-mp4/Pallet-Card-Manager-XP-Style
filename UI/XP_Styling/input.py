import tkinter as tk
from .colors import XP_BORDER_COLOR, XP_BEIGE, XP_BTN_BG
from .fonts import XP_FONT
from .title_bar import XPTitleBar

class XPInputDialog(tk.Toplevel):
    def __init__(self, parent, title, prompt, initial_value="", trigger_key=None):
        super().__init__(parent)
        self.result = None; self.trigger_key = trigger_key
        self.withdraw(); self.configure(bg=XP_BORDER_COLOR); self.overrideredirect(True)
        parent.update_idletasks(); w, h = 400, 180 
        try: x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (w // 2); y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (h // 2)
        except: x = (self.winfo_screenwidth() // 2) - (w // 2); y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")
        
        main_frame = tk.Frame(self, bg=XP_BORDER_COLOR, bd=3); main_frame.pack(fill=tk.BOTH, expand=True)
        self.title_bar = XPTitleBar(main_frame, self, app_instance=self, title_text=title, close_func=self.cancel)
        content = tk.Frame(main_frame, bg=XP_BEIGE, padx=20, pady=20); content.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(content, text=prompt, bg=XP_BEIGE, font=("Tahoma", 10, "bold")).pack(anchor="w", pady=(0, 10))
        self.entry = tk.Entry(content, font=("Tahoma", 11), bd=2, relief="sunken"); self.entry.insert(0, initial_value); self.entry.pack(fill=tk.X, pady=5); self.entry.select_range(0, tk.END)
        
        btn_frame = tk.Frame(content, bg=XP_BEIGE); btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))
        tk.Button(btn_frame, text="OK", width=12, command=self.ok, bg=XP_BTN_BG, relief="raised", bd=2, font=XP_FONT).pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_frame, text="Cancel", width=12, command=self.cancel, bg=XP_BTN_BG, relief="raised", bd=2, font=XP_FONT).pack(side=tk.RIGHT, padx=5)
        
        self.bind("<Escape>", self.cancel); self.bind("<Return>", self.ok)
        if self.trigger_key:
            clean_key = self.trigger_key.strip("<>")
            self.bind(f"<KeyPress-{clean_key}>", lambda e: "break")
            self.bind(f"<KeyRelease-{clean_key}>", lambda e: self.unlock_trigger(e, clean_key))
            if clean_key == "Return": self.unbind("<Return>")
        self.deiconify(); self.lift(); self.grab_set(); self.after(20, self.set_focus); self.wait_window(self)

    def unlock_trigger(self, event, key_name):
        self.unbind(f"<KeyPress-{key_name}>"); self.unbind(f"<KeyRelease-{key_name}>")
        if key_name == "Return": self.bind("<Return>", self.ok)

    def set_focus(self):
        try: self.entry.focus_force()
        except: pass

    def ok(self, event=None):
        self.result = self.entry.get(); self.destroy()

    def cancel(self, event=None):
        self.result = None; self.destroy()