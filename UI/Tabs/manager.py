import tkinter as tk
from UI.XP_Styling.colors import XP_BEIGE
from .renderer import TabRenderer

class TabManager:
    def __init__(self, parent_frame, app_manager):
        self.app = app_manager
        
        self.container = tk.Frame(parent_frame, bg=XP_BEIGE)
        self.container.pack(side=tk.TOP, fill=tk.X, pady=(0, 2))
        
        self.renderer = TabRenderer(self.container)
        
        self.container.bind("<Configure>", lambda e: self.refresh())

    def refresh(self):
        """Redraws all tabs based on current app state."""
        self.renderer.clear()

        self.renderer.draw_tabs(
            sheet_names=self.app.sheet_order,
            active_name=self.app.active_sheet_name,
            on_click=self.app.switch_to_sheet,
            on_drag=self.on_tab_drag
        )

    def on_tab_drag(self, event, dragged_name):
        """Handles reordering logic."""
        target_widget = self.container.winfo_containing(event.x_root, event.y_root)
        
        if target_widget and target_widget.master == self.container:
            target_text = target_widget.cget("text").strip()
            
            if target_text != dragged_name and target_text in self.app.sheet_order:
                idx_src = self.app.sheet_order.index(dragged_name)
                idx_dst = self.app.sheet_order.index(target_text)
                
                self.app.sheet_order[idx_src], self.app.sheet_order[idx_dst] = \
                    self.app.sheet_order[idx_dst], self.app.sheet_order[idx_src]
                
                self.refresh()