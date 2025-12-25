import tkinter as tk
from .defaults import DEFAULT_HOTKEY_MAP, PERMANENT_HOTKEYS

class HotkeyLogic:
    def __init__(self, app):
        self.app = app
        self.key_map = DEFAULT_HOTKEY_MAP.copy()
        self.permanent = PERMANENT_HOTKEYS

    def bind_all(self):
        """Binds all configured hotkeys to the root window."""
        # Unbind first to avoid duplicates if reloading
        # (Tkinter overwrites callbacks on same key, so strictly unbinding isn't always fatal, but good practice)
        
        # 1. Tab Navigation
        self.app.root.bind(self.key_map["Next Tab"], lambda e: self.app.next_tab())
        self.app.root.bind(self.key_map["Previous Tab"], lambda e: self.app.prev_tab())
        
        # 2. Sheet Operations
        self.app.root.bind(self.key_map["Rename Sheet"], self.app.sheets_manager.prompt_rename)
        
        # 3. Active Sheet Specifics (Delegates to currently open sheet)
        self.app.root.bind(self.key_map["Add Rows"], lambda e: self.app.call_active_sheet("prompt_add_rows"))
        self.app.root.bind(self.key_map["Delete Rows"], lambda e: self.app.call_active_sheet("prompt_delete_rows"))
        self.app.root.bind(self.key_map["Clear Sheet"], lambda e: self.app.call_active_sheet("prompt_clear_sheet"))
        self.app.root.bind(self.key_map["Print Manager"], lambda e: self.app.call_active_sheet("open_print_manager"))
        
        # 4. Tools
        # Note: We import SearchDialog inside the lambda to avoid circular imports during setup
        from UI.Main_Layout.search import SearchDialog
        self.app.root.bind(self.key_map["Find"], lambda e: SearchDialog(self.app.root, self.app))

    def update_key(self, action_name, new_key_string):
        """Updates a specific action to a new key and rebinds."""
        if action_name in self.key_map:
            # Unbind old key (Optional, but clean)
            old_key = self.key_map[action_name]
            try: self.app.root.unbind(old_key)
            except: pass
            
            self.key_map[action_name] = new_key_string
            self.bind_all() # Re-bind everything to ensure consistency

    def reset_to_defaults(self):
        self.key_map = DEFAULT_HOTKEY_MAP.copy()
        self.bind_all()