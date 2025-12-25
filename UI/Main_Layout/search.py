import tkinter as tk
from tkinter import ttk
from UI.XP_Styling.colors import XP_BORDER_COLOR, XP_BEIGE, XP_BTN_BG
from UI.XP_Styling.fonts import XP_FONT
from UI.XP_Styling.title_bar import XPTitleBar

class SearchDialog(tk.Toplevel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.results_cache = [] 
        
        self.withdraw()
        self.overrideredirect(True)
        self.configure(bg=XP_BORDER_COLOR)
        
        width, height = 900, 600

        try:
            x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (width // 2)
            y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (height // 2)

        except:
            x = (self.winfo_screenwidth() // 2) - (width // 2)
            y = (self.winfo_screenheight() // 2) - (height // 2)

        self.geometry(f"{width}x{height}+{x}+{y}")

        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("Treeview", 
                        background="white", 
                        fieldbackground="white", 
                        font=("Tahoma", 9), 
                        rowheight=20,
                        borderwidth=0)
        
        style.configure("Treeview.Heading", 
                        font=("Tahoma", 9, "bold"), 
                        background=XP_BTN_BG, 
                        relief="raised")
        
        main_border = tk.Frame(self, bg=XP_BORDER_COLOR, bd=3)
        main_border.pack(fill=tk.BOTH, expand=True)
        
        self.title_bar = XPTitleBar(main_border, self, title_text="Find in Inventory", close_func=self.destroy)

        self.content = tk.Frame(main_border, bg=XP_BEIGE)
        self.content.pack(fill=tk.BOTH, expand=True)

        lbl = tk.Label(self.content, 
                       text="Type to search (Use Up/Down arrows to select):", 
                       font=XP_FONT, 
                       bg=XP_BEIGE, 
                       fg="black")
        lbl.pack(pady=(10, 5), padx=10, anchor="w")

        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.on_search_change)
        self.entry = tk.Entry(self.content, textvariable=self.search_var, 
                              font=("Tahoma", 11), relief="sunken", bd=2, bg="white")
        self.entry.pack(fill=tk.X, padx=10, pady=5)
        self.entry.focus_set()

        tree_frame = tk.Frame(self.content, bd=2, relief="sunken", bg="white")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        cols = ("Sheet", "Column", "Row", "Value")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=15)
        
        self.tree.heading("Sheet", text="Sheet Name")
        self.tree.column("Sheet", width=120, anchor="w")
        self.tree.heading("Column", text="Column")
        self.tree.column("Column", width=120, anchor="w")
        self.tree.heading("Row", text="Row #")
        self.tree.column("Row", width=80, anchor="center")
        self.tree.heading("Value", text="Content")
        self.tree.column("Value", width=350, anchor="w")
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.entry.bind("<Down>", self.navigate_results)
        self.entry.bind("<Up>", self.navigate_results)
        self.entry.bind("<Return>", self.trigger_jump)
        self.tree.bind("<Return>", self.trigger_jump)
        self.tree.bind("<Double-1>", self.trigger_jump)
        self.bind("<Escape>", lambda e: self.destroy())

        self.deiconify()

    def on_search_change(self, *args):
        query = self.search_var.get()
        self.tree.delete(*self.tree.get_children())
        self.results_cache = []
        
        if hasattr(self.app, 'search_engine'):
            results = self.app.search_engine.search(query)
            
            for item in results:
                self.tree.insert("", "end", values=(
                    item['sheet'], 
                    item['column'], 
                    item['row_display'], 
                    item['value']
                ))
                self.results_cache.append((item['sheet'], item['raw_r'], item['raw_c']))
            
            if self.tree.get_children(): 
                self.tree.selection_set(self.tree.get_children()[0])

    def navigate_results(self, event):
        if hasattr(self.app, 'search_engine'):
            return self.app.search_engine.navigate_results(self.tree, event)

    def trigger_jump(self, event=None):
        selected_item = self.tree.selection()
        
        if not selected_item: return
        
        idx = self.tree.index(selected_item[0])
        
        if idx < len(self.results_cache):
            sheet_name, row, col = self.results_cache[idx]
            self.app.jump_to_cell(sheet_name, row, col)
            self.destroy()