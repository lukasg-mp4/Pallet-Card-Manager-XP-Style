class DataInjector:
    def inject(self, editor, rows):
        editor.commit_edit()
        editor.history.record("Excel Import")
        
        needed = len(rows)
        if needed > len(editor.data):
            for _ in range(needed - len(editor.data) + 5):
                editor.data.append(["" for _ in editor.headers])

        for i, item in enumerate(rows):
            editor.data[i][1] = item["Larousse"]
            editor.data[i][2] = item["BBD"]
            editor.data[i][3] = item["Qty"]
            editor.data[i][4] = "1"

        editor.redraw()