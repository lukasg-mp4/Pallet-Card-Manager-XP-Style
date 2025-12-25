from tkinter import messagebox
from UI.XP_Styling.notifications import XPInfoDialog, XPErrorDialog
from .loader import ExcelLoader
from .processor import DataProcessor
from .injector import DataInjector

class ExcelManager:
    def __init__(self, app):
        self.app = app
        self.loader = ExcelLoader()
        self.processor = DataProcessor()
        self.injector = DataInjector()

    def prompt_import(self):
        # 1. Get Active Sheet
        name = self.app.active_sheet_name
        if not name or name not in self.app.sheets:
            messagebox.showwarning("Import", "No active sheet selected.")
            return
        
        # 2. Get File
        path = self.loader.prompt_file(self.app.root)
        if not path: return

        try:
            # 3. Load & Process
            df = self.loader.load_raw_dataframe(path)
            rows = self.processor.process(df)
            
            if not rows:
                XPInfoDialog(self.app.root, "Import", "No valid data rows found.")
                return

            # 4. Inject
            self.injector.inject(self.app.sheets[name], rows)
            
            # 5. Finalize
            self.app.trigger_refresh()
            self.app.auto_save_trigger()
            XPInfoDialog(self.app.root, "Success", f"Imported {len(rows)} rows.")
            
        except Exception as e:
            XPErrorDialog(self.app.root, "Error", str(e))