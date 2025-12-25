import tkinter as tk
from tkinter import ttk
from UI.XP_Styling.colors import XP_BORDER_COLOR, XP_BEIGE, XP_BTN_BG
from UI.XP_Styling.fonts import XP_FONT, XP_FONT_BOLD
from UI.XP_Styling.title_bar import XPTitleBar
from UI.XP_Styling.confirmation import XPMessageBox
from UI.XP_Styling.notifications import XPInfoDialog

class HistoryWindow(tk.Toplevel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.withdraw(); self.overrideredirect(True); self.configure(bg=XP_BORDER_COLOR)
        
        w, h = 700, 500

        try: x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (w // 2); y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (h // 2)
        except: x = (self.winfo_screenwidth() // 2) - (w // 2); y = (self.winfo_screenheight() // 2) - (h // 2)

        self.geometry(f"{w}x{h}+{x}+{y}")

        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure(
            "Treeview", 
            background="white", 
            fieldbackground="white", 
            font=XP_FONT, 
            rowheight=20,
            borderwidth=0
        )
        
        style.configure(
            "Treeview.Heading", 
            font=XP_FONT_BOLD, 
            background=XP_BTN_BG, 
            relief="raised"
        )

        main = tk.Frame(self, bg=XP_BORDER_COLOR, bd=3); main.pack(fill=tk.BOTH, expand=True)
        XPTitleBar(main, self, app_instance=self, title_text="Edit History", close_func=self.destroy)
        
        content = tk.Frame(main, bg=XP_BEIGE, padx=10, pady=10); content.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(content, text="Select a version and click 'Jump' to restore that state.", bg=XP_BEIGE, font=XP_FONT).pack(anchor="w", pady=(0, 5))

        cols = ("Date", "Time", "Action", "Sheet")
        self.tree = ttk.Treeview(content, columns=cols, show="headings", height=15)
        
        self.tree.heading("Date", text="Date")
        self.tree.heading("Time", text="Time")
        self.tree.heading("Action", text="Action Description")
        self.tree.heading("Sheet", text="Sheet")
        
        self.tree.column("Date", width=90, anchor="center")
        self.tree.column("Time", width=90, anchor="center")
        self.tree.column("Action", width=300, anchor="w")
        self.tree.column("Sheet", width=120, anchor="w")
        
        vsb = ttk.Scrollbar(content, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.populate()

        btn_frame = tk.Frame(main, bg=XP_BEIGE, height=40)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=10)

        if not self.app.history_restored_flag:
            self.btn_restore = tk.Button(btn_frame, 
                                         text="Restore Previous Session History", 
                                         command=self.do_restore_history,
                                         bg=XP_BTN_BG, 
                                         relief="raised", 
                                         bd=2, 
                                         font=XP_FONT)
            
            self.btn_restore.pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(btn_frame, 
                  text="Jump to Version", 
                  command=self.do_jump, 
                  bg=XP_BTN_BG, 
                  relief="raised", 
                  bd=2, font=XP_FONT_BOLD).pack(side=tk.LEFT)
        
        tk.Button(btn_frame, 
                  text="Close", 
                  command=self.destroy, 
                  bg=XP_BTN_BG, 
                  relief="raised", 
                  bd=2, 
                  font=XP_FONT).pack(side=tk.RIGHT)
        
        self.deiconify(); self.lift(); self.grab_set()

    def populate(self):
        for i in self.tree.get_children(): self.tree.delete(i)

        for idx, entry in enumerate(reversed(self.app.global_history)):
            real_idx = len(self.app.global_history) - 1 - idx
            self.tree.insert("", "end", iid=str(real_idx), values=(
                entry.get('date', '-'), entry.get('timestamp', '-'), 
                entry.get('action', '-'), entry.get('target_sheet', '-')
            ))

    def do_restore_history(self):
        if XPMessageBox(self, "Restore History", "Load history from the previous session?\n(This will merge it with current history)").result:
            count = self.app.load_previous_history()

            if count > 0:
                self.populate()
                self.btn_restore.pack_forget()
                XPInfoDialog(self, "Success", f"Restored {count} entries from previous session.")

            else:
                XPInfoDialog(self, "Info", "No previous history found.")

    def do_jump(self):
        sel = self.tree.selection()
        if not sel: return

        idx = int(sel[0])

        if XPMessageBox(self, "Confirm Jump", "Are you sure? This will overwrite the current session\nwith the data from the selected point in history.").result:
            target = self.app.global_history[idx]
            self.app.restore_snapshot(target)
            self.destroy()