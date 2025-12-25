from UI.XP_Styling.input import XPInputDialog

class DeleteRows:
    def __init__(self, app):
        self.app = app

    def execute(self):
        name = self.app.active_sheet_name
        if not name or name not in self.app.sheets: return

        editor = self.app.sheets[name]

        current_count = len(editor.data)
        d = XPInputDialog(self.app.root, "Delete Rows", "Remove how many rows from bottom?", initial_value="1")

        if d.result and d.result.isdigit():
            count = int(d.result)
            
            if count <= 0 or count > current_count: return
            
            editor.commit_edit()
            editor.history.record(f"Deleted {count} Rows")
            
            self.app.log_snapshot(f"Deleted {count} Rows from '{name}'", target_sheet=name)
            
            editor.data = editor.data[:-count]
            if editor.cur_row >= len(editor.data):
                editor.cur_row = max(0, len(editor.data) - 1)
                
            editor.redraw()
            self.app.data_manager.save_all()
            self.app.trigger_refresh()