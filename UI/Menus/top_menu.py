import tkinter as tk
from UI.XP_Styling.colors import XP_BEIGE
from UI.XP_Styling.fonts import XP_FONT

# Optional External Imports
try:
    from UI.Main_Layout.hotkeys import HotkeyManager
    from UI.Main_Layout.history import HistoryWindow
except ImportError:
    HotkeyManager = None
    HistoryWindow = None

class TopMenuBar(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=XP_BEIGE, height=40)
        self.app = app
        self.pack(fill=tk.X, side=tk.TOP, pady=2)
        
        self.setup_left_buttons()
        self.setup_print_status()

    def setup_left_buttons(self):

        tk.Label(self, 
                 text="PLT CARD MANAGER", 
                 bg=XP_BEIGE, 
                 font=("Tahoma", 12, "bold")).pack(side=tk.LEFT, padx=10)

        btn_add_tab = tk.Button(self, 
                                text="+ New Company Sheet", 
                                command=self.app.prompt_new_tab, 
                                bg="white", 
                                relief="raised", 
                                bd=2, 
                                font=XP_FONT)
        
        btn_add_tab.pack(side=tk.LEFT, padx=10, pady=5)
    
        btn_del_tab = tk.Button(self, 
                                text="- Delete Company Sheet", 
                                command=self.app.prompt_delete_tab, 
                                bg="white", 
                                relief="raised", 
                                bd=2, 
                                font=XP_FONT)
        
        btn_del_tab.pack(side=tk.LEFT, padx=(0, 10), pady=5)
        
        btn_import = tk.Button(self, text="Import Excel", command=self.trigger_import,
                               bg="white", relief="raised", bd=2, font=XP_FONT)
        btn_import.pack(side=tk.LEFT, padx=5, pady=5)

        tk.Button(self, 
                  text="Hotkeys", 
                  command=self.open_hotkeys,
                  bg="white", 
                  relief="raised", 
                  bd=2, 
                  font=XP_FONT).pack(side=tk.LEFT, padx=5, pady=5)

        tk.Button(self, 
                  text="Edit History", 
                  command=self.open_history,
                  bg="#eef", 
                  relief="raised", 
                  bd=2, 
                  font=XP_FONT).pack(side=tk.LEFT, padx=5, pady=5)

        tk.Label(self, 
                 text="(Ctrl+Arrows to Switch | Ctrl+F to Search)", 
                 bg=XP_BEIGE, 
                 fg="#555555", 
                 font=("Tahoma", 9)).pack(side=tk.LEFT, padx=5)

    def setup_print_status(self):
        self.print_var = tk.StringVar(value="Printing Status: Idle")
        self.lbl_print = tk.Label(self, textvariable=self.print_var, bg=XP_BEIGE, fg="#444444", font=("Tahoma", 9, "bold"))
        self.lbl_print.pack(side=tk.LEFT, padx=(15, 5))

        self.btn_cancel = tk.Button(self, 
                                    text="Cancel Print", 
                                    command=self.app.cancel_printing,
                                    bg="#ffcccc", 
                                    relief="raised", 
                                    bd=2, font=("Tahoma", 8), 
                                    state="disabled")
        self.btn_cancel.pack(side=tk.LEFT, padx=5)

    def trigger_import(self):

        if hasattr(self.app, 'excel_manager') and self.app.excel_manager:
            self.app.excel_manager.prompt_import()

        else:
            print("Excel Manager not loaded yet.")

    def open_hotkeys(self):
        if HotkeyManager: HotkeyManager(self.winfo_toplevel(), self.app)

    def open_history(self):
        if HistoryWindow: HistoryWindow(self.winfo_toplevel(), self.app)

    def update_print_status(self, text, color="black", is_printing=False):
        self.print_var.set(text)
        self.lbl_print.config(fg=color)

        if is_printing:
            self.btn_cancel.config(state="normal", bg="#ff9999")
            
        else:
            self.btn_cancel.config(state="disabled", bg="#ffcccc")