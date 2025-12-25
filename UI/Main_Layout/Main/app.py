import tkinter as tk
import ctypes

# UI Components
from UI.XP_Styling.colors import XP_BEIGE, XP_BORDER_COLOR
from UI.XP_Styling.title_bar import XPTitleBar
from UI.XP_Styling.window_resizer import Resizer
from UI.Main_Layout.preview import PreviewPane
from UI.Tabs.manager import TabManager
from UI.Menus.top_menu import TopMenuBar

# Main Sub-Modules
from .sheet_ops import SheetManager
from Print_Manager.service import PrintService

# Util Modules
from Util.UI_Functionality.Hotkeys.manager import HotkeyLogic
from Util.UI_Functionality.History.session_log import SessionLog
from Util.UI_Functionality.History.persistence import DiskManager
from Util.UI_Functionality.Navigation.preview_scroller import PreviewScroller
from Util.UI_Functionality.Navigation.tab_navigator import TabNavigator
from Util.UI_Functionality.Sheets.manager import RowManager
from Util.UI_Functionality.Navigation.search_engine import SearchEngine

# Popups
from UI.Main_Layout.hotkeys import HotkeyManager
from UI.Main_Layout.search import SearchDialog

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()
        self.root.overrideredirect(True)
        self.root.configure(bg=XP_BORDER_COLOR)
        
        self.excel_manager = None
        self.print_manager = None

        self.sheets = {}
        self.sheet_order = []
        self.active_sheet_name = None
        self.maximized = False
        
        # --- FIX: Safe Default Geometry ---
        self.old_geometry = "1100x750+100+100"
        
        self.preview_timer = None
        self.dragging = False

        self.permanent_hotkeys = {
            "Move Down / Row Menu": "Enter (Hold)",
            "Move Right / Col Menu": "Tab (Hold)",
            "Move Up": "Ctrl + Enter",
            "Move Left": "Ctrl + Tab",
            "Delete Selection": "Delete / Backspace",
            "Undo Sheet Change": "Ctrl + Shift + Z",
            "Redo Sheet Change": "Ctrl + Shift + Y"
        }

        self.hotkey_map = {
            "Rename Sheet": "<Control-r>", 
            "Next Tab": "<Control-Right>",
            "Previous Tab": "<Control-Left>", 
            "Find": "<Control-f>", 
            "Print Manager": "<Control-p>",
            "Add Rows": "<Control-n>",
            "Delete Rows": "<Control-d>",
            "Clear Sheet": "<Control-Shift-C>"
        }
        self.default_hotkeys = self.hotkey_map.copy()

        self.data_manager = DiskManager(self)
        self.print_service = PrintService(self)
        self.sheets_manager = SheetManager(self)
        self.hotkeys = HotkeyLogic(self)
        self.history_log = SessionLog(self)
        self.preview_scroller = PreviewScroller(self)
        self.tab_navigator = TabNavigator(self)
        self.row_manager = RowManager(self)
        self.search_engine = SearchEngine(self)
        
        # Aliases
        self.global_history = self.history_log.history 
        self.restore_snapshot = self.history_log.restore_snapshot 
        self.log_snapshot = self.history_log.log_snapshot
        self.load_previous_history = self.data_manager.load_old_history
        self.update_hotkey = self.hotkeys.update_key

        self.setup_ui()
        self.bind_keys()
        self.data_manager.load_sheets()
        
        self.root.after(100, self.root.deiconify)
        self.root.after(200, self.force_taskbar_icon) 
        
        self.history_log.log_snapshot("Session Start")
        self.toggle_maximize()

    @property
    def history_restored_flag(self):
        return self.data_manager.history_restored_flag

    def setup_ui(self):
        border = tk.Frame(self.root, bg=XP_BORDER_COLOR, bd=3)
        border.pack(fill=tk.BOTH, expand=True)
        self.title_bar = XPTitleBar(border, self.root, self, "Multi-Sheet Manager", close_func=self.on_close)
        
        self.content = tk.Frame(border, bg=XP_BEIGE)
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

    def bind_keys(self):
        self.hotkeys.bind_all()
        self.root.bind("<Control-Shift-Z>", self.sheets_manager.undo_action)
        self.root.bind("<Control-Shift-Y>", self.sheets_manager.redo_action)

    def prompt_new_tab(self): self.sheets_manager.prompt_new()
    def prompt_delete_tab(self): self.sheets_manager.prompt_delete()
    def switch_to_sheet(self, name): self.sheets_manager.switch_to_sheet(name)
    def cancel_printing(self): self.print_service.cancel()
    def start_print_job(self, s, i): self.print_service.start_job(s, i)
    def auto_save_trigger(self): self.data_manager.save_all()
    
    def next_tab(self): self.tab_navigator.next_tab()
    def prev_tab(self): self.tab_navigator.prev_tab()

    def jump_to_cell(self, sheet, r, c):
        self.switch_to_sheet(sheet)
        self.sheets[sheet].jump_to_specific_cell(r, c)
        
    def jump_to_row(self, r):
        if self.active_sheet_name: 
            self.sheets[self.active_sheet_name].jump_to_specific_cell(r, 0, trigger_refresh=False)

    def call_active_sheet(self, method_name):
        if method_name in ["prompt_add_rows", "prompt_delete_rows", "prompt_clear_sheet"]:
            getattr(self.row_manager, method_name)()
        elif method_name == "open_print_manager":
             if self.active_sheet_name:
                 self.sheets[self.active_sheet_name].open_print_manager()
        elif self.active_sheet_name:
            if hasattr(self.sheets[self.active_sheet_name], method_name):
                getattr(self.sheets[self.active_sheet_name], method_name)()
    
    def trigger_full_refresh(self):
        if self.preview_timer: self.root.after_cancel(self.preview_timer)
        self.preview_timer = self.root.after(50, self._do_refresh)
    
    def trigger_refresh(self): self.trigger_full_refresh()

    def _do_refresh(self):
        if self.active_sheet_name:
            rows = self.sheets[self.active_sheet_name].get_completed_rows()
            cur_r = self.sheets[self.active_sheet_name].cur_row
            self.preview.refresh(rows, cur_r)

    # --- FIX: Restored Logic to prevent 1x1 glitch ---
    def toggle_maximize(self, event=None, use_curtain=True):
        if self.maximized:
            # RESTORE to old geometry
            target_geo = self.old_geometry
            # Failsafe: if geometry is missing or garbage (1x1), use default
            if not target_geo or target_geo.startswith("1x1+"): 
                target_geo = "1100x750+100+100"
            
            self.root.geometry(target_geo)
            self.title_bar.btn_max.config(text="□")
            self.maximized = False
        else:
            # MAXIMIZE
            current_geo = self.root.geometry()
            # Only save if it looks like a real window, not a minimized 1x1 state
            if not current_geo.startswith("1x1+"): 
                self.old_geometry = current_geo
            
            w = self.root.winfo_screenwidth()
            h = self.root.winfo_screenheight()
            self.root.geometry(f"{w}x{h}+0+0")
            
            self.title_bar.btn_max.config(text="❐")
            self.maximized = True
            
        self.trigger_full_refresh()

    def minimize_app(self):
        self.root.overrideredirect(False); self.root.iconify()
        self.root.bind("<Map>", self.restore_frame)

    def restore_frame(self, e):
        if self.root.state() == 'normal':
            self.root.overrideredirect(True); self.root.unbind("<Map>")
            self.force_taskbar_icon()

    def force_taskbar_icon(self):
        try:
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            if hwnd == 0: hwnd = self.root.winfo_id()
            GWL_EXSTYLE = -20; WS_EX_APPWINDOW = 0x00040000
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            if not (style & WS_EX_APPWINDOW):
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_APPWINDOW)
            ctypes.windll.user32.SetParent(hwnd, 0)
            SWP_NOMOVE = 0x0002; SWP_NOSIZE = 0x0001; SWP_NOZORDER = 0x0004; SWP_FRAMECHANGED = 0x0020; SWP_SHOWWINDOW = 0x0040
            ctypes.windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED | SWP_SHOWWINDOW)
        except Exception as e: print(f"Taskbar Error: {e}")
    
    def stop_timers(self):
        if self.preview_timer: self.root.after_cancel(self.preview_timer)
    
    def request_debounce_refresh(self): self.trigger_full_refresh()

    def on_close(self):
        self.data_manager.save_all()
        self.root.destroy()