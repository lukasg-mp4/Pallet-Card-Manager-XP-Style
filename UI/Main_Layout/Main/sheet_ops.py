import tkinter as tk
import copy
from UI.Sheet_Editor.editor import SheetEditor
from UI.XP_Styling.input import XPInputDialog
from UI.XP_Styling.delete_sheet_dialog import XPDeleteSheetDialog
from UI.XP_Styling.confirmation import XPMessageBox

class SheetManager:
    def __init__(self, app):
        self.app = app
        self.undo_stack = []
        self.redo_stack = []

    def switch_to_sheet(self, name):
        if name not in self.app.sheets: return
        self.app.active_sheet_name = name
        for w in self.app.sheet_holder.winfo_children(): 
            w.pack_forget()
        self.app.sheets[name].pack(fill=tk.BOTH, expand=True)
        self.app.sheets[name].refocus_cell()
        self.app.tabs.refresh()
        self.app.trigger_refresh()

    def add_tab(self, name, initial_data=None, select_tab=True, record_undo=True):
        if name in self.app.sheets: return
        
        if record_undo:
            # --- FIX: Use app alias ---
            self.app.log_snapshot(f"Created Sheet '{name}'", target_sheet=name)
            self.undo_stack.append(("ADD", name, None))
            self.redo_stack.clear()
            
        self.app.sheets[name] = SheetEditor(self.app.sheet_holder, self.app, name, initial_data)
        self.app.sheet_order.append(name)
        
        if select_tab: self.switch_to_sheet(name)
        else: self.app.tabs.refresh()
        self.app.data_manager.save_all()

    def prompt_new(self):
        d = XPInputDialog(self.app.root, "New", "Sheet Name:")
        if d.result: self.add_tab(d.result)

    def prompt_delete(self):
        if not self.app.sheets: return
        current = self.app.active_sheet_name if self.app.active_sheet_name else self.app.sheet_order[0]
        d = XPDeleteSheetDialog(self.app.root, list(self.app.sheets.keys()), current)
        if d.result:
            if XPMessageBox(self.app.root, "Confirm", f"Delete '{d.result}'?").result:
                self.perform_delete(d.result)

    def perform_delete(self, name, record_undo=True):
        if name not in self.app.sheets: return
        
        saved_data = None
        if record_undo:
            saved_data = copy.deepcopy(self.app.sheets[name].get_sheet_data())
            # --- FIX: Use app alias ---
            self.app.log_snapshot(f"Deleted Sheet '{name}'", target_sheet=name)
            self.undo_stack.append(("DELETE", name, saved_data))
            self.redo_stack.clear()

        self.app.sheets[name].destroy()
        del self.app.sheets[name]
        if name in self.app.sheet_order: self.app.sheet_order.remove(name)
        
        if not self.app.sheets: self.add_tab("Default Sheet", record_undo=False)
        elif self.app.active_sheet_name == name: self.switch_to_sheet(self.app.sheet_order[0])
        else: self.app.tabs.refresh()
        self.app.data_manager.save_all()

    def prompt_rename(self, event=None):
        if not self.app.active_sheet_name: return
        old = self.app.active_sheet_name
        d = XPInputDialog(self.app.root, "Rename", "New Name:", initial_value=old)
        if d.result and d.result != old and d.result not in self.app.sheets:
            new = d.result
            editor = self.app.sheets[old]; editor.update_name(new)
            self.app.sheets[new] = editor; del self.app.sheets[old]
            idx = self.app.sheet_order.index(old); self.app.sheet_order[idx] = new
            self.switch_to_sheet(new); self.app.data_manager.save_all()

    def undo_action(self, event=None):
        if not self.undo_stack: return "break"
        action, name, data = self.undo_stack.pop()
        
        if action == "ADD":
            self.perform_delete(name, record_undo=False)
            self.redo_stack.append(("ADD", name, None))
        elif action == "DELETE":
            self.add_tab(name, data, select_tab=True, record_undo=False)
            self.redo_stack.append(("DELETE", name, data))
        return "break"

    def redo_action(self, event=None):
        if not self.redo_stack: return "break"
        action, name, data = self.redo_stack.pop()
        
        if action == "ADD":
            self.add_tab(name, data, select_tab=True, record_undo=False)
            self.undo_stack.append(("ADD", name, None))
        elif action == "DELETE":
            self.perform_delete(name, record_undo=False)
            self.undo_stack.append(("DELETE", name, data))
        return "break"