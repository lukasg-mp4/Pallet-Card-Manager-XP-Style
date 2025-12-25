from UI.XP_Styling.confirmation import XPMessageBox

class ClearSheet:
    def __init__(self, app):
        self.app = app

    def execute(self):
        name = self.app.active_sheet_name
        if not name or name not in self.app.sheets: return

        editor = self.app.sheets[name]

        if XPMessageBox(self.app.root, "Clear Sheet", "Are you sure you want to clear this sheet?").result:
            editor.commit_edit()
            editor.history.record("Cleared Sheet")
            
            self.app.log_snapshot(f"Cleared Sheet '{name}'", target_sheet=name)
            
            editor.data = [["" for _ in editor.headers] for _ in range(40)]
            editor.cur_row = 0
            editor.cur_col = 0
            
            editor.redraw()
            self.app.data_manager.save_all()
            self.app.trigger_refresh()