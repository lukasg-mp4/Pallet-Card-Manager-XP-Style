import datetime
import copy

class SessionLog:
    def __init__(self, app):
        self.app = app
        self.history = []
        self.max_entries = 100

    def log_snapshot(self, description, target_sheet=None):
        """Captures the state of ALL sheets."""
        now = datetime.datetime.now()
        
        state_snapshot = []
        # We grab data from the App's sheet manager
        for name in self.app.sheet_order:
            if name in self.app.sheets:
                # Deep copy is essential here
                data = copy.deepcopy(self.app.sheets[name].get_sheet_data())
                state_snapshot.append((name, data))
        
        entry = {
            'date': now.strftime("%d/%m/%Y"),
            'timestamp': now.strftime("%H:%M:%S"),
            'action': description,
            'target_sheet': target_sheet,
            'state': state_snapshot
        }
        
        self.history.append(entry)
        if len(self.history) > self.max_entries:
            self.history.pop(0)

    def restore_snapshot(self, snapshot_entry):
        """Restores the app to the state in the snapshot."""
        # 1. Clear UI
        for name in list(self.app.sheets.keys()):
            self.app.sheets[name].destroy()
        self.app.sheets.clear()
        self.app.sheet_order.clear()
        
        # 2. Restore Sheets
        state = snapshot_entry['state']
        for name, data in state:
            # We bypass the "User Add" logic and go straight to internal add
            self.app.sheets_manager.add_tab(name, data, select_tab=False, record_undo=False)
            
        # 3. Focus correct sheet
        target = snapshot_entry.get('target_sheet')
        if not target or target not in self.app.sheets:
            if self.app.sheet_order: target = self.app.sheet_order[0]
            
        self.app.active_sheet_name = None 
        self.app.switch_to_sheet(target)
        
        # 4. Save this state immediately
        self.app.data_manager.save_all()