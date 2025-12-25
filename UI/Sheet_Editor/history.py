import copy

class HistoryManager:
    def __init__(self, editor):
        self.editor = editor
        self.undo_stack = []
        self.redo_stack = []

    def record(self, description="Cell Edit", target_row=None, target_col=None):
        """Snapshots the current data before a change is made."""
        if len(self.undo_stack) > 50: 
            self.undo_stack.pop(0)
            
        r = target_row if target_row is not None else self.editor.cur_row
        c = target_col if target_col is not None else self.editor.cur_col
        
        # Snapshot state
        snapshot = (copy.deepcopy(self.editor.data), (r, c), description)
        self.undo_stack.append(snapshot)
        self.redo_stack.clear()

    def perform_undo(self):
        if not self.undo_stack: return "break"
            
        # 1. Peek at the action we are about to undo
        _, _, description = self.undo_stack[-1]
        
        # 2. GLOBAL LOGGING: If it's a major change (not just typing), log it to the main history
        if description != "Cell Edit":
            self.editor.app_manager.log_snapshot(
                f"Undid: {description} in '{self.editor.sheet_name}'", 
                target_sheet=self.editor.sheet_name
            )

        # 3. Save current state to Redo Stack
        current_snapshot = (copy.deepcopy(self.editor.data), (self.editor.cur_row, self.editor.cur_col), description)
        self.redo_stack.append(current_snapshot)
        
        # 4. Restore state from Undo Stack
        prev_data, (saved_row, saved_col), _ = self.undo_stack.pop()
        self.editor.data = prev_data
        
        # 5. Update UI
        if 0 <= saved_row < len(self.editor.data) and 0 <= saved_col < len(self.editor.headers):
            self.editor.jump_to_specific_cell(saved_row, saved_col)
        else:
            self.editor.cur_row = min(self.editor.cur_row, len(self.editor.data) - 1)
            self.editor.hide_entry(); self.editor.redraw()
            
        self.editor.app_manager.auto_save_trigger()
        return "break"

    def perform_redo(self):
        if not self.redo_stack: return "break"
            
        # 1. Peek at action
        _, _, description = self.redo_stack[-1]
        
        # 2. GLOBAL LOGGING
        if description != "Cell Edit":
            self.editor.app_manager.log_snapshot(
                f"Redid: {description} in '{self.editor.sheet_name}'", 
                target_sheet=self.editor.sheet_name
            )

        # 3. Save current state to Undo Stack
        current_snapshot = (copy.deepcopy(self.editor.data), (self.editor.cur_row, self.editor.cur_col), description)
        self.undo_stack.append(current_snapshot)
        
        # 4. Restore state from Redo Stack
        next_data, (saved_row, saved_col), _ = self.redo_stack.pop()
        self.editor.data = next_data
        
        # 5. Update UI
        if 0 <= saved_row < len(self.editor.data) and 0 <= saved_col < len(self.editor.headers):
            self.editor.jump_to_specific_cell(saved_row, saved_col)
        else:
            self.editor.hide_entry(); self.editor.redraw()
            
        self.editor.app_manager.auto_save_trigger()
        return "break"