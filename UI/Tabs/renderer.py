import tkinter as tk
from UI.XP_Styling.colors import XP_BTN_BG, XP_BEIGE
from UI.XP_Styling.fonts import XP_FONT, XP_FONT_BOLD
from .config import measure_text_width, TAB_HEIGHT, TAB_PAD_X, UNIFIED_BUFFER

class TabRenderer:
    def __init__(self, container):
        self.container = container

    def clear(self):
        for w in self.container.winfo_children():
            w.destroy()

    def draw_tabs(self, sheet_names, active_name, on_click, on_drag):
        if not sheet_names: return

        # 1. Calculate Standard Width based on longest name (Professional Look)
        max_px = max([measure_text_width(name) for name in sheet_names])
        unified_w = max_px + UNIFIED_BUFFER

        # 2. Layout Calculation
        cur_x, cur_y = TAB_PAD_X, 2
        cont_w = self.container.winfo_width()
        if cont_w < 100: cont_w = 1000

        for name in sheet_names:
            is_active = (name == active_name)
            
            # Create the Tab (Label acting as Button)
            lbl = tk.Label(self.container, text=f"  {name}  ", 
                           bg="white" if is_active else XP_BTN_BG,
                           font=XP_FONT_BOLD if is_active else XP_FONT,
                           relief="sunken" if is_active else "raised", bd=2)
            
            # Wrap to next row if needed
            if cur_x + unified_w > cont_w:
                cur_x = TAB_PAD_X
                cur_y += TAB_HEIGHT + 2
            
            lbl.place(x=cur_x, y=cur_y, height=TAB_HEIGHT, width=unified_w)
            
            # Bind Events
            lbl.bind("<Button-1>", lambda e, n=name: on_click(n))
            lbl.bind("<B1-Motion>", lambda e, n=name: on_drag(e, n))
            
            cur_x += unified_w + TAB_PAD_X

        # Resize container to fit rows
        self.container.config(height=cur_y + TAB_HEIGHT + 4)