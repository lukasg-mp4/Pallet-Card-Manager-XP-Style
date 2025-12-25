import tkinter as tk
from tkinter import ttk, messagebox
from UI.XP_Styling.colors import XP_BORDER_COLOR, XP_BEIGE, XP_BTN_BG
from UI.XP_Styling.title_bar import XPTitleBar

class HotkeyManager(tk.Toplevel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        
        self.withdraw(); self.overrideredirect(True); self.configure(bg=XP_BORDER_COLOR)
        
        width, height = 500, 550

        try:
            x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (width // 2)
            y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (height // 2)
        except:
            x = (self.winfo_screenwidth() // 2) - (width // 2)
            y = (self.winfo_screenheight() // 2) - (height // 2)

        self.geometry(f"{width}x{height}+{x}+{y}")

        self.main_border = tk.Frame(self, bg=XP_BORDER_COLOR, bd=3)
        self.main_border.pack(fill=tk.BOTH, expand=True)
        self.title_bar = XPTitleBar(self.main_border, self, self, "Configure Hotkeys", close_func=self.destroy)
        
        self.content = tk.Frame(self.main_border, bg=XP_BEIGE, padx=10, pady=10)
        self.content.pack(fill=tk.BOTH, expand=True)

        cols = ("Action", "Current Key")
        self.tree = ttk.Treeview(self.content, columns=cols, show="headings", height=12)
        self.tree.heading("Action", text="Action")
        self.tree.heading("Current Key", text="Current Key")
        self.tree.column("Action", width=250)
        self.tree.column("Current Key", width=150, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.populate_tree()

        self.tree.tag_configure('header', background="#dcdcdc", font=("Tahoma", 9, "bold"))
        self.tree.tag_configure('permanent', foreground="#666666")

        btn_frame = tk.Frame(self.content, bg=XP_BEIGE)
        btn_frame.pack(fill=tk.X, pady=10)

        tk.Button(btn_frame, text="Edit Selected", 
                  command=self.prompt_edit_key, 
                  bg=XP_BTN_BG, relief="raised", 
                  bd=2, 
                  font=("Tahoma", 9, "bold")).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, 
                  text="Reset Defaults", 
                  command=self.reset_defaults, 
                  bg=XP_BTN_BG, 
                  relief="raised", 
                  bd=2, 
                  font=("Tahoma", 9)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, 
                  text="Close", 
                  command=self.destroy, 
                  bg=XP_BTN_BG, 
                  relief="raised", 
                  bd=2, 
                  font=("Tahoma", 9)).pack(side=tk.RIGHT, padx=5)
        
        self.deiconify(); self.lift(); self.grab_set(); self.wait_window(self)

    def populate_tree(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        
        self.tree.insert("", "end", values=("--- PERMANENT KEYBINDS ---", ""), tags=('header',))

        for action, key in self.app.permanent_hotkeys.items():
            self.tree.insert("", "end", values=(action, key), tags=('permanent',))

        self.tree.insert("", "end", values=("", "")) 
        self.tree.insert("", "end", values=("--- EDITABLE KEYBINDS ---", ""), tags=('header',))
        
        for action, key in self.app.hotkey_map.items():
            self.tree.insert("", "end", values=(action, self.format_key_display(key)), tags=('editable',))

    def prompt_edit_key(self):
        selected = self.tree.selection()

        if not selected: return

        item = self.tree.item(selected[0])
        tags = item.get('tags', [])

        if 'permanent' in tags or 'header' in tags:
            messagebox.showinfo("Locked", "This keybinding is permanent and cannot be changed.")
            return
        
        action = item['values'][0]
        
        capturer = tk.Toplevel(self)
        capturer.title("Press New Key")
        capturer.geometry("300x150")

        x = self.winfo_x() + 100; y = self.winfo_y() + 100
        capturer.geometry(f"+{x}+{y}")
        capturer.configure(bg=XP_BEIGE)
        capturer.overrideredirect(True)

        f = tk.Frame(capturer, 
                     bg=XP_BORDER_COLOR, 
                     bd=2); 
        
        f.pack(fill=tk.BOTH, expand=True)

        in_f = tk.Frame(f, bg=XP_BEIGE); in_f.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(in_f, 
                 text=f"Press new key combination for:\n'{action}'", 
                 bg=XP_BEIGE, 
                 font=("Tahoma", 10, "bold")).pack(pady=20)
        
        tk.Label(in_f, 
                 text="(Press Esc to Cancel)", 
                 bg=XP_BEIGE, 
                 font=("Tahoma", 8)).pack(pady=5)
        
        capturer.bind("<KeyPress>", lambda e: self.capture_key(e, action, capturer))
        capturer.focus_force(); capturer.grab_set()

    def format_key_display(self, key_str):
        raw = key_str.replace("<", "").replace(">", "")
        parts = raw.split("-")
        formatted_parts = []

        for p in parts:

            if p.lower() == "control": formatted_parts.append("Ctrl")
            elif p.lower() == "shift": formatted_parts.append("Shift")
            elif p.lower() == "alt": formatted_parts.append("Alt")
            else: formatted_parts.append(p.title())

        return " + ".join(formatted_parts)

    def capture_key(self, event, action_name, window):

        if event.keysym in ('Control_L', 'Control_R', 'Shift_L', 'Shift_R', 'Alt_L', 'Alt_R'): return
        if event.keysym == 'Escape': window.destroy(); return

        parts = []

        if event.state & 0x0004: parts.append("Control")
        if event.state & 0x0001: parts.append("Shift")
        if event.state & 0x20000: parts.append("Alt")

        key = event.keysym

        if len(key) == 1: key = key.lower()
        
        parts.append(key)
        new_bind_str = "<" + "-".join(parts) + ">"
        
        self.app.update_hotkey(action_name, new_bind_str)
        window.destroy()
        self.populate_tree()

    def reset_defaults(self):
        if messagebox.askyesno("Reset", "Reset editable hotkeys to default?"):
            self.app.hotkey_map = self.app.default_hotkeys.copy()
            self.app.apply_hotkeys()
            self.populate_tree()