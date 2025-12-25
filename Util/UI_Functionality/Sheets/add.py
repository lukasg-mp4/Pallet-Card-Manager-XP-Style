from UI.XP_Styling.input import XPInputDialog

class AddRows:
    def __init__(self, app):
        self.app = app

    def execute(self):
        name = self.app.active_sheet_name
        if not name or name not in self.app.sheets: return
        editor = self.app.sheets[name]

        d = XPInputDialog(self.app.root, "Add Rows", "How many rows to add?", initial_value="1")
        if d.result and d.result.isdigit():
            count = int(d.result)
            if count > 0:
                editor.commit_edit()
                editor.history.record(f"Added {count} Rows")
                
                # --- FIX: Log to Global History ---
                self.app.log_snapshot(f"Added {count} Rows to '{name}'", target_sheet=name)
                
                for _ in range(count): 
                    editor.data.append(["" for _ in editor.headers])
                
                editor.redraw()
                self.app.data_manager.save_all()
                self.app.trigger_refresh()