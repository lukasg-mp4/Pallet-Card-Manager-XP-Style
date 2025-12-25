class TabNavigator:
    def __init__(self, app):
        self.app = app

    def next_tab(self):
        if not self.app.sheet_order: return

        try:
            curr_idx = self.app.sheet_order.index(self.app.active_sheet_name)
            next_idx = (curr_idx + 1) % len(self.app.sheet_order)
            self.app.switch_to_sheet(self.app.sheet_order[next_idx])

        except: pass

    def prev_tab(self):
        if not self.app.sheet_order: return

        try:
            curr_idx = self.app.sheet_order.index(self.app.active_sheet_name)
            prev_idx = (curr_idx - 1) % len(self.app.sheet_order)
            self.app.switch_to_sheet(self.app.sheet_order[prev_idx])
            
        except: pass