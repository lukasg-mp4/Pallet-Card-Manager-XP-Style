class SearchEngine:
    def __init__(self, app):
        self.app = app

    def search(self, query):
        """
        Scans all sheets for the query string.
        Returns a list of dictionaries containing result info.
        """
        results = []
        if not query: 
            return results
        
        q = query.lower()
        
        # Iterate through all sheets
        for sheet_name, editor in self.app.sheets.items():
            if not hasattr(editor, 'data'): continue
            
            for r_idx, row_list in enumerate(editor.data):
                for c_idx, cell_value in enumerate(row_list):
                    val_str = str(cell_value)
                    
                    if q in val_str.lower():
                        # Determine Column Name
                        if c_idx < len(editor.headers):
                            col_name = editor.headers[c_idx]
                        else:
                            col_name = "Unknown"
                            
                        results.append({
                            'sheet': sheet_name,
                            'column': col_name,
                            'row_display': f"Row {r_idx + 1}",
                            'value': val_str,
                            'raw_r': r_idx,
                            'raw_c': c_idx
                        })
        return results

    def navigate_results(self, tree, event):
        """Handles moving selection in Treeview using Up/Down from Entry."""
        items = tree.get_children()
        if not items: return
        
        selection = tree.selection()
        if not selection:
            next_item = items[0]
        else:
            current_idx = items.index(selection[0])
            if event.keysym == "Down":
                next_idx = min(current_idx + 1, len(items) - 1)
            else: # Up
                next_idx = max(current_idx - 1, 0)
            next_item = items[next_idx]
        
        tree.selection_set(next_item)
        tree.see(next_item)
        return "break"