import tkinter as tk
from .config import (
    FIXED_COL_0_WIDTH, ROW_HEIGHT, HEADER_HEIGHT, GAP_WIDTH, ROW_GAP,
    XP_BEIGE, PILLAR_COLOR, CELL_BG_ALT, HIGHLIGHT_COLOR, YELLOW_HIGHLIGHT,
    XP_FONT_BOLD, XP_FONT_CELL
)

class GridRenderer:
    def __init__(self, editor):
        self.ed = editor 

    def redraw(self):
        if self.ed.editor_window_id: 
            self.ed.canvas.delete(self.ed.editor_window_id)
            self.ed.editor_window_id = None
        self.ed.canvas.delete("all")
        self.ed.header_canvas.delete("all") 
        
        self._calc_dimensions()
        self._draw_backgrounds()
        self._draw_grid_lines()
        self._draw_row_headers()
        self._draw_content()
        self._draw_column_headers()
        
        if self.ed.editor_window_id and self.ed.floating_entry.winfo_viewable():
             self.ed.canvas.tag_raise(self.ed.editor_window_id)

    def _calc_dimensions(self):
        vis_w = self.ed.canvas.winfo_width()
        if vis_w < 100: vis_w = 1100 

        min_w = 115
        total_content_w = FIXED_COL_0_WIDTH + (len(self.ed.headers) * min_w)
        
        avail_w = vis_w - FIXED_COL_0_WIDTH - 5 
        if total_content_w > vis_w:
            self.ed.col_widths = [min_w] * len(self.ed.headers)
            self.ed.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
            self.final_w = total_content_w
        else:
            self.ed.h_scroll.pack_forget()
            dyn_w = max(min_w, avail_w // len(self.ed.headers))
            self.ed.col_widths = [dyn_w] * len(self.ed.headers)
            self.final_w = FIXED_COL_0_WIDTH + sum(self.ed.col_widths)
        
        self.total_h = (len(self.ed.data) * (ROW_HEIGHT + ROW_GAP))
        self.ed.canvas.config(scrollregion=(0, 0, self.final_w, self.total_h))
        self.ed.header_canvas.config(scrollregion=(0, 0, self.final_w, HEADER_HEIGHT))

        self.col_x_starts = []
        curr = FIXED_COL_0_WIDTH
        for w in self.ed.col_widths: 
            self.col_x_starts.append(curr)
            curr += w

    def _draw_backgrounds(self):
        has_sel = (len(self.ed.selected_rows) > 0 or len(self.ed.selected_cols) > 0)
        has_cell_sel = (len(self.ed.selected_cells) > 0)
        
        for r_idx in range(len(self.ed.data)):
            y = (r_idx * (ROW_HEIGHT + ROW_GAP))
            
            if r_idx in self.ed.selected_rows: fill = HIGHLIGHT_COLOR
            elif r_idx == self.ed.cur_row and not (has_sel or has_cell_sel): fill = YELLOW_HIGHLIGHT
            elif r_idx % 2 != 0: fill = CELL_BG_ALT
            else: fill = "white"
            
            self.ed.canvas.create_rectangle(0, y, self.final_w, y + ROW_HEIGHT, fill=fill, outline="")

            if has_cell_sel:
                row_cells = [c for (r, c) in self.ed.selected_cells if r == r_idx]
                for c_idx in row_cells:
                    if 0 <= c_idx < len(self.ed.col_widths):
                        x = self.col_x_starts[c_idx]
                        w = self.ed.col_widths[c_idx]
                        self.ed.canvas.create_rectangle(x, y, x+w, y + ROW_HEIGHT, fill=HIGHLIGHT_COLOR, outline="")

        for c_idx in self.ed.selected_cols:
            if 0 <= c_idx < len(self.ed.col_widths):
                x = self.col_x_starts[c_idx]
                w = self.ed.col_widths[c_idx]
                self.ed.canvas.create_rectangle(x, 0, x+w, self.total_h, fill=HIGHLIGHT_COLOR, outline="")

    def _draw_grid_lines(self):
        # 1. Horizontal Lines
        for r_idx in range(len(self.ed.data)):
            y = (r_idx * (ROW_HEIGHT + ROW_GAP))
            self.ed.canvas.create_line(0, y, self.final_w, y, fill="#808080")
            self.ed.canvas.create_line(0, y+1, self.final_w, y+1, fill="#404040")
            y_bottom = y + ROW_HEIGHT
            self.ed.canvas.create_line(0, y_bottom-1, self.final_w, y_bottom-1, fill="#FFFFFF")

        # 2. Vertical Lines (The critical 3D pillar look)
        curr_x = FIXED_COL_0_WIDTH
        for i, w in enumerate(self.ed.col_widths):
            line_x_left = curr_x + GAP_WIDTH/2
            line_x_left_2 = line_x_left + 1
            line_x_right = curr_x + w - GAP_WIDTH/2
            
            # Draw Main Vertical Pillars
            self.ed.canvas.create_line(line_x_left, 0, line_x_left, self.total_h, fill="#808080")
            self.ed.canvas.create_line(line_x_left_2, 0, line_x_left_2, self.total_h, fill="#404040")
            
            if i < len(self.ed.col_widths) - 1:
                self.ed.canvas.create_line(line_x_right, 0, line_x_right, self.total_h, fill="#FFFFFF")
                
            # Draw Cell Dividers for rows
            for r_idx in range(len(self.ed.data)):
                y = (r_idx * (ROW_HEIGHT + ROW_GAP))
                y_bottom = y + ROW_HEIGHT
                self.ed.canvas.create_line(line_x_left, y, line_x_left, y_bottom, fill="#808080")
                self.ed.canvas.create_line(line_x_left_2, y, line_x_left_2, y_bottom, fill="#404040")
                if i < len(self.ed.col_widths) - 1:
                    self.ed.canvas.create_line(line_x_right, y, line_x_right, y_bottom, fill="#FFFFFF")
            
            curr_x += w

        # 3. Draw Pillar Backgrounds (Fills the gap with gray)
        self.ed.canvas.create_rectangle(FIXED_COL_0_WIDTH - (GAP_WIDTH/2), 0, FIXED_COL_0_WIDTH + (GAP_WIDTH/2), self.total_h, fill=PILLAR_COLOR, outline="")
        curr_x = FIXED_COL_0_WIDTH
        for w in self.ed.col_widths[:-1]:
            curr_x += w
            self.ed.canvas.create_rectangle(curr_x - (GAP_WIDTH/2), 0, curr_x + (GAP_WIDTH/2), self.total_h, fill=PILLAR_COLOR, outline="")

    def _draw_row_headers(self):
        for r_idx in range(len(self.ed.data)):
            y = (r_idx * (ROW_HEIGHT + ROW_GAP))
            is_pressed = (r_idx in self.ed.selected_rows)
            bg = "#c0c0c0" if is_pressed else XP_BEIGE
            
            # Row Header Box
            self.ed.canvas.create_rectangle(2, y+1, FIXED_COL_0_WIDTH - (GAP_WIDTH/2), y + ROW_HEIGHT - 1, fill=bg, outline="")
            
            # 3D Effect for buttons
            btn_right = FIXED_COL_0_WIDTH - (GAP_WIDTH/2)
            btn_btm = y + ROW_HEIGHT - 1
            if is_pressed:
                self.ed.canvas.create_line(2, y+1, btn_right, y+1, fill="#808080")
                self.ed.canvas.create_line(2, y+1, 2, btn_btm, fill="#808080")
                self.ed.canvas.create_line(2, btn_btm, btn_right, btn_btm, fill="white")
            else:
                self.ed.canvas.create_line(2, y+1, btn_right, y+1, fill="white")
                self.ed.canvas.create_line(2, y+1, 2, btn_btm, fill="white")
                self.ed.canvas.create_line(2, btn_btm, btn_right, btn_btm, fill="#808080")
                self.ed.canvas.create_line(btn_right, y+1, btn_right, btn_btm, fill="#808080")

            self.ed.canvas.create_text(FIXED_COL_0_WIDTH/2 - 2, y + ROW_HEIGHT/2, text=f"{r_idx+1}.", font=XP_FONT_BOLD)

    def _draw_content(self):
        for r_idx, row_data in enumerate(self.ed.data):
            y_mid = (r_idx * (ROW_HEIGHT + ROW_GAP)) + (ROW_HEIGHT / 2)
            curr_x = FIXED_COL_0_WIDTH
            for c_idx, val in enumerate(row_data):
                w = self.ed.col_widths[c_idx]
                is_editing = (r_idx == self.ed.cur_row and c_idx == self.ed.cur_col and self.ed.floating_entry.winfo_viewable())
                if not is_editing and val:
                    self.ed.canvas.create_text(curr_x + w/2, y_mid + 1, text=val, font=XP_FONT_CELL, anchor="center")
                curr_x += w - 1

    def _draw_column_headers(self):
        self.ed.header_canvas.create_rectangle(0, 0, self.final_w + 100, HEADER_HEIGHT, fill=XP_BEIGE, outline="")
        
        def btn(x, y, w, h, text, pressed):
            self.ed.header_canvas.create_rectangle(x, y, x+w, y+h, fill=XP_BEIGE, outline="")
            if pressed:
                self.ed.header_canvas.create_line(x, y, x+w, y, fill="#808080")
                self.ed.header_canvas.create_line(x, y, x, y+h, fill="#808080")
                self.ed.header_canvas.create_line(x+w, y+h, x+w, y, fill="white")
                self.ed.header_canvas.create_line(x+w, y+h, x, y+h, fill="white")
                f = XP_FONT_BOLD; offset = 1
            else:
                self.ed.header_canvas.create_line(x, y, x+w, y, fill="white")
                self.ed.header_canvas.create_line(x, y, x, y+h, fill="white")
                self.ed.header_canvas.create_line(x+w, y+h, x+w, y, fill="#404040")
                self.ed.header_canvas.create_line(x, y+h, x+w, y+h, fill="#404040")
                self.ed.header_canvas.create_line(x+w-1, y+1, x+w-1, y+h-1, fill="#808080")
                f = XP_FONT_BOLD; offset = 0
            self.ed.header_canvas.create_text(x + w/2 + offset, y + h/2 + offset, text=text, font=f)

        btn(1, 1, FIXED_COL_0_WIDTH - 2, HEADER_HEIGHT - 2, "#", False)
        curr_x = FIXED_COL_0_WIDTH
        for i, h in enumerate(self.ed.headers):
            w = self.ed.col_widths[i]
            btn_w = w
            if not self.ed.h_scroll.winfo_viewable() and i == len(self.ed.headers) - 1: 
                btn_w = self.ed.canvas.winfo_width() - curr_x
            btn(curr_x + 1, 1, btn_w - 2, HEADER_HEIGHT - 2, h, (i in self.ed.selected_cols))
            curr_x += w