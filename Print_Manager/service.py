from UI.XP_Styling.notifications import XPErrorDialog
from .gdi import GDIPrinter

class PrintService:
    def __init__(self, app):
        self.app = app
        self.gdi = GDIPrinter()
        self.queue = []
        self.timer = None
        self.target_sheet = None
        self.countdown = 0
        self.cur_doc_idx = 0
        self.cur_copy_idx = 0

    def start_job(self, sheet_name, items):
        if not items: return
        self.queue = items
        self.target_sheet = sheet_name
        self.countdown = 5
        self.app.top_menu.update_print_status("Starting in 5s...", "red", True)
        self.update_countdown()

    def update_countdown(self):
        if self.countdown > 0:
            self.app.top_menu.update_print_status(f"Starting in {self.countdown}s...", "red", True)
            self.countdown -= 1
            self.timer = self.app.root.after(1000, self.update_countdown)
        else:
            self.app.top_menu.update_print_status("Printing...", "blue", True)
            self.cur_doc_idx = 0; self.cur_copy_idx = 0
            self.app.root.after(500, self.process_queue)

    def cancel(self):
        if self.timer: self.app.root.after_cancel(self.timer)
        self.queue = []
        self.app.top_menu.update_print_status("Cancelled", "red", False)
        self.app.root.after(3000, lambda: self.app.top_menu.update_print_status("Idle", "black", False))

    def process_queue(self):
        if not self.queue: self.finish(); return
        
        item = self.queue[0]
        status = f"Printing: {item['larousse']} ({self.cur_copy_idx+1}/{item['copies']})"
        self.app.top_menu.update_print_status(status, "blue", True)
        self.app.root.update_idletasks()
        
        if not self.gdi.send_page(item):
            self.cancel()
            XPErrorDialog(self.app.root, "Error", "Printer Error.\nCheck connection.")
            return

        self.cur_copy_idx += 1
        if self.cur_copy_idx >= item['copies']:
            done = self.queue.pop(0)
            if self.target_sheet in self.app.sheets:
                self.app.sheets[self.target_sheet].clear_row_data(done['row_idx'])
            self.cur_doc_idx += 1; self.cur_copy_idx = 0
            
        self.timer = self.app.root.after(100, self.process_queue)

    def finish(self):
        self.app.top_menu.update_print_status("Completed", "green", False)
        self.app.trigger_refresh()
        self.app.root.after(5000, lambda: self.app.top_menu.update_print_status("Idle", "black", False))