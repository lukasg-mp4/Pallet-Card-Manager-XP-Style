import os
import json

class DiskManager:
    def __init__(self, app):
        self.app = app
        self.data_file = "inventory_data.json"
        self.history_file = "history_log.json"
        self.history_restored_flag = False

    def load_sheets(self):
        """Loads sheet data from JSON into the App."""
        if os.path.exists(self.data_file):

            try:
                with open(self.data_file, "r") as f:
                    data = json.load(f)

                    for name, sheet_data in data.items():
                        self.app.sheets_manager.add_tab(name, sheet_data, False, False)

            except: pass
        
        if not self.app.sheets:
            self.app.sheets_manager.add_tab("Default Sheet", record_undo=False)
            
        if self.app.sheet_order:
            self.app.sheets_manager.switch_to_sheet(self.app.sheet_order[0])

    def save_all(self):
        """Saves current sheets and session history to disk."""
        d = {k: v.get_sheet_data() for k, v in self.app.sheets.items()}

        try:
            with open(self.data_file, "w") as f: json.dump(d, f)

        except: pass

        try:
            with open(self.history_file, "w") as f: 
                json.dump(self.app.history_log.history, f)

        except: pass

    def load_old_history(self):
        """Merges previous session history into current."""
        if self.history_restored_flag: return 0

        if not os.path.exists(self.history_file): return 0

        try:
            with open(self.history_file, "r") as f:
                old_entries = json.load(f)
            
            if old_entries:
                self.app.history_log.history = old_entries + self.app.history_log.history
                self.history_restored_flag = True
                return len(old_entries)
            
        except: pass
        
        return 0