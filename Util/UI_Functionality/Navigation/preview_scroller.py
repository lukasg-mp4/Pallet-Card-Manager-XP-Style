class PreviewScroller:
    def __init__(self, app):
        self.app = app


    def next_doc(self):
        pane = self.app.preview
        data = pane.cached_data
        if not data: return
        new_idx = pane.view_index + 1
        if new_idx >= len(data): new_idx = 0 
        self._sync(new_idx, data)


    def prev_doc(self):
        pane = self.app.preview
        data = pane.cached_data
        if not data: return
        new_idx = pane.view_index - 1
        if new_idx < 0: new_idx = len(data) - 1
        self._sync(new_idx, data)


    def _sync(self, idx, data):
        self.app.preview.view_index = idx
        self.app.preview.redraw()
        target_item = data[idx]
        name = self.app.active_sheet_name
        if name and name in self.app.sheets:
            editor = self.app.sheets[name]
            editor.jump_to_specific_cell(
                target_item['row_idx'], 
                editor.cur_col, 
                trigger_refresh=False 
            )