import tkinter as tk
import json
import os
import copy
import datetime
from tkinter import ttk, messagebox

# UI Components
from UI.XP_Styling.colors import XP_BEIGE, XP_BORDER_COLOR, XP_BTN_BG
from UI.XP_Styling.title_bar import XPTitleBar
from UI.XP_Styling.window_resizer import Resizer
from UI.XP_Styling.input import XPInputDialog
from UI.XP_Styling.delete_sheet_dialog import XPDeleteSheetDialog
from UI.XP_Styling.confirmation import XPMessageBox

from UI.Sheet_Editor.editor import SheetEditor
from UI.Main_Layout.preview import PreviewPane
from UI.Main_Layout.hotkeys import HotkeyManager
from UI.Main_Layout.search import SearchDialog
from UI.Main_Layout.history import HistoryWindow

from UI.Tabs.manager import TabManager
from UI.Menus.top_menu import TopMenuBar

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()
        self.root.overrideredirect(True)
        self.root.configure(bg=XP_BORDER_COLOR)
        
        self.excel_manager = None 
        self.print_manager = None

        self.data_file = "inventory_data.json"
        self.sheets = {}
        self.sheet_order = []
        self.active_sheet_name = None
        self.global_history = []
        self.maximized = False
        self.old_geometry = "1100x750+100+100"

        self.hotkey_map = {
            "Rename Sheet": "<Control-r>", "Next Tab": "<Control-Right>",
            "Find": "<Control-f>", "Add Rows": "<Control-n>"
        }

        self.setup_ui()
        self.apply_hotkeys()
        self.load_data()
        
        self.root.after(100, self.root.deiconify)
        self.log_snapshot("Session Start")

    def setup_ui(self):
        main_border = tk.Frame(self.root, bg=XP_BORDER_COLOR, bd=3)
        main_border.pack(fill=tk.BOTH, expand=True)

        self.title_bar = XPTitleBar(main_border, 
                                    self.root, self, 
                                    "Multi-Sheet Manager", 
                                    close_func=self.on_close)
        
        self.content = tk.Frame(main_border, bg=XP_BEIGE)
        self.content.pack(fill=tk.BOTH, expand=True)
        
        self.top_menu = TopMenuBar(self.content, self)

        body = tk.Frame(self.content, bg=XP_BEIGE, relief="raised", bd=3)
        body.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tabs = TabManager(body, self)
        
        split = tk.Frame(body, bg=XP_BEIGE)
        split.pack(fill=tk.BOTH, expand=True)
        
        self.preview = PreviewPane(split, self)
        self.preview.pack(side=tk.RIGHT, fill=tk.Y, padx=2)
        
        self.sheet_holder = tk.Frame(split, bg=XP_BEIGE, relief="raised", bd=2)
        self.sheet_holder.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.resizer = Resizer(self.root, self)
        
    def switch_to_sheet(self, name):
        if name not in self.sheets: return

        self.active_sheet_name = name

        for w in self.sheet_holder.winfo_children(): w.pack_forget()

        self.sheets[name].pack(fill=tk.BOTH, expand=True)
        self.tabs.render()
        self.trigger_full_refresh()

    def add_tab(self, name, data=None):
        if name in self.sheets: return

        self.sheets[name] = SheetEditor(self.sheet_holder, self, name, data)
        self.sheet_order.append(name)
        self.switch_to_sheet(name)

    def prompt_new_tab(self):
        d = XPInputDialog(self.root, "New", "Sheet Name:")
        if d.result: self.add_tab(d.result); self.log_snapshot(f"Created {d.result}")

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as f:
                data = json.load(f)
                for k, v in data.items(): self.add_tab(k, v)

        if not self.sheets: self.add_tab("Default")

    def save_data(self):
        data = {k: v.get_sheet_data() for k, v in self.sheets.items()}
        with open(self.data_file, "w") as f: json.dump(data, f)

    def auto_save_trigger(self): self.save_data()
    
    def trigger_full_refresh(self):
        if self.active_sheet_name:
            rows = self.sheets[self.active_sheet_name].get_completed_rows()
            cur_r = self.sheets[self.active_sheet_name].cur_row
            self.preview.refresh(rows, cur_r)

    def jump_to_row(self, row_idx):
        if self.active_sheet_name:
            self.sheets[self.active_sheet_name].jump_to_specific_cell(row_idx, 0)

    def jump_to_cell(self, sheet, r, c):
        self.switch_to_sheet(sheet)
        self.sheets[sheet].jump_to_specific_cell(r, c)

    def apply_hotkeys(self):
        self.root.bind(self.hotkey_map["Find"], lambda e: SearchDialog(self.root, self))
        self.root.bind(self.hotkey_map["Next Tab"], lambda e: self.next_tab())
    
    def next_tab(self):
        if not self.sheet_order: return

        idx = (self.sheet_order.index(self.active_sheet_name) + 1) % len(self.sheet_order)
        self.switch_to_sheet(self.sheet_order[idx])

    def log_snapshot(self, desc):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.global_history.append({'timestamp': now, 'action': desc})

    def toggle_maximize(self):
        self.maximized = not self.maximized

        if self.maximized:
            self.old_geometry = self.root.geometry()
            self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
            
        else:
            self.root.geometry(self.old_geometry)

    def minimize_app(self):
        self.root.overrideredirect(False); self.root.iconify()
        self.root.bind("<Map>", self.restore_frame)

    def restore_frame(self, e):
        if self.root.state() == 'normal':
            self.root.overrideredirect(True); self.root.unbind("<Map>")

    def on_close(self):
        self.save_data(); self.root.destroy()