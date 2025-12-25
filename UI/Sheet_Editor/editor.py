import tkinter as tk
from tkinter import messagebox

from .config import *
from .history import HistoryManager
from .renderer import GridRenderer
from UI.XP_Styling.input import XPInputDialog
from UI.XP_Styling.confirmation import XPMessageBox

from UI.Main_Layout.Print_Dialog.dialog import PrintDialog

class SheetEditor(tk.Frame):
    def __init__(self, parent_notebook, app_manager, sheet_name, initial_data=None):
        super().__init__(parent_notebook)
        self.app_manager = app_manager
        self.sheet_name = sheet_name
        self.configure(bg=XP_BEIGE)

        self.headers = HEADERS
        self.col_widths = COL_WIDTHS_DEFAULT
        self.cur_row = 0; self.cur_col = 0
        self.selected_rows = set(); self.selected_cols = set(); self.selected_cells = set()
        self.selection_anchor = None; self.pre_drag_selection = set()
        
        self.hold_timer = None
        self.current_held_key = None
        self.resize_timer = None
        self.editor_window_id = None

        self.history = HistoryManager(self)
        self.renderer = GridRenderer(self)

        self.data = []

        if initial_data:
            for row_vals in initial_data:

                row = [str(val) if val is not None else "" for val in row_vals]
                while len(row) < len(self.headers): row.append("")

                self.data.append(row)

        if not self.data:
            for _ in range(40): self.data.append(["" for _ in self.headers])

        self.setup_ui()

    def setup_ui(self):
        self.btn_print = tk.Button(self, 
                                   text=f"Print Menu For: '{self.sheet_name}'", 
                                  command=self.open_print_manager, 
                                  bg="#ffdddd", 
                                  relief="raised", 
                                  bd=2, 
                                  font=XP_FONT)
        
        self.btn_print.pack(fill=tk.X, padx=5, pady=5)

        container = tk.Frame(self, bg=XP_BEIGE)
        container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        hc_frame = tk.Frame(container, bg=XP_BEIGE, height=HEADER_HEIGHT)
        hc_frame.pack(side=tk.TOP, fill=tk.X)
        self.header_canvas = tk.Canvas(hc_frame, bg=XP_BEIGE, height=HEADER_HEIGHT, highlightthickness=0, bd=0)
        self.header_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        body_frame = tk.Frame(container, bg=XP_BEIGE)
        body_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(body_frame, bg=PILLAR_COLOR, highlightthickness=0, bd=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.v_scroll = tk.Scrollbar(body_frame, orient="vertical", command=self.canvas.yview)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.config(yscrollcommand=self.v_scroll.set)

        self.h_scroll = tk.Scrollbar(container, orient="horizontal", command=self.canvas.xview)
        self.canvas.config(xscrollcommand=self.on_body_scroll_x)

        self.entry_var = tk.StringVar()
        self.floating_entry = tk.Entry(self.canvas, 
                                       textvariable=self.entry_var, 
                                      font=XP_FONT_CELL, 
                                      justify="center", 
                                      bd=0, 
                                      relief="flat", 
                                      highlightthickness=0)
        
        self.bind_events()
        btm = tk.Frame(self, bg=XP_BEIGE, height=35)
        btm.pack(fill=tk.X, side=tk.BOTTOM)

        tk.Button(btm, 
                  text="+ Add Rows", 
                  command=self.app_manager.row_manager.prompt_add_rows, 
                  bg=XP_BTN_BG, 
                  font=XP_FONT, 
                  relief="raised", 
                  bd=2).pack(side=tk.LEFT, padx=(10, 5), pady=5)
        
        tk.Button(btm, 
                  text="- Delete Rows", 
                  command=self.app_manager.row_manager.prompt_delete_rows, 
                  bg=XP_BTN_BG, 
                  font=XP_FONT, 
                  relief="raised", 
                  bd=2).pack(side=tk.LEFT, padx=5, pady=5)
        
        tk.Button(btm, 
                  text="x Clear Sheet", 
                  command=self.app_manager.row_manager.prompt_clear_sheet, 
                  bg=XP_BTN_BG, 
                  font=XP_FONT, 
                  relief="raised", 
                  bd=2).pack(side=tk.RIGHT, padx=10, pady=5)

    def bind_events(self):
        self.canvas.bind("<Configure>", lambda e: self.on_resize_request())
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", lambda e: setattr(self, 'selection_anchor', None))
        self.header_canvas.bind("<Button-1>", self.on_header_click)
        
        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))

        self.canvas.bind("<Control-z>", lambda e: self.history.perform_undo())
        self.canvas.bind("<Control-y>", lambda e: self.history.perform_redo())
        self.floating_entry.bind("<Control-z>", lambda e: self.history.perform_undo())
        self.floating_entry.bind("<Control-y>", lambda e: self.history.perform_redo())

        self.canvas.bind("<Delete>", self.delete_selection)
        self.canvas.bind("<BackSpace>", self.delete_selection)
        self.canvas.bind("<KeyRelease-Control_L>", self.on_ctrl_release)
        
        self.floating_entry.bind("<FocusOut>", self.hide_entry)
        
        self.floating_entry.bind("<KeyPress-Return>", lambda e: self.on_key_press(e, "Return"))
        self.floating_entry.bind("<KeyRelease-Return>", lambda e: self.on_hold_key_release(e, "Return"))
        self.floating_entry.bind("<KeyPress-Tab>", lambda e: self.on_key_press(e, "Tab"))
        self.floating_entry.bind("<KeyRelease-Tab>", lambda e: self.on_hold_key_release(e, "Tab"))
        
        self.floating_entry.bind("<Control-Return>", lambda e: self.move_cursor(-1, 0))
        self.floating_entry.bind("<Control-Tab>", lambda e: self.move_cursor(0, -1))
        self.floating_entry.bind("<KeyRelease>", self.on_generic_key_release)

    def on_key_press(self, event, key_type):
        if self.current_held_key == key_type: return "break"

        self.current_held_key = key_type
        self.hold_timer = self.after(500, lambda: self.trigger_hold_action(key_type))

        return "break"

    def trigger_hold_action(self, key_type):
        self.hold_timer = None

        if key_type == "Return": self.open_goto_row()
        elif key_type == "Tab": self.open_goto_col()

    def on_hold_key_release(self, event, key_type):
        if self.current_held_key == key_type:

            if self.hold_timer:
                self.after_cancel(self.hold_timer)
                self.hold_timer = None

                if key_type == "Return": self.move_cursor(1, 0) # Down
                elif key_type == "Tab": self.move_cursor(0, 1)  # Right

            self.current_held_key = None

    def open_goto_row(self):
        d = XPInputDialog(self.winfo_toplevel(), "Go to Row", "Number:", trigger_key="Return")
        self.current_held_key = None; self.hold_timer = None

        if d.result and d.result.isdigit():
            r = int(d.result) - 1

            if 0 <= r < len(self.data): self.jump_to_specific_cell(r, self.cur_col)

        self.refocus_cell()

    def open_goto_col(self):
        d = XPInputDialog(self.winfo_toplevel(), "Go to Column", "Number:", trigger_key="Tab")
        self.current_held_key = None; self.hold_timer = None

        if d.result and d.result.isdigit():
            c = int(d.result) - 1

            if 0 <= c < len(self.headers): self.jump_to_specific_cell(self.cur_row, c)

        self.refocus_cell()

    def redraw(self): self.renderer.redraw()

    def on_resize_request(self):
        if self.resize_timer: self.after_cancel(self.resize_timer)

        self.resize_timer = self.after(20, self.redraw)

    def on_click(self, event):
        self.canvas.focus_set()
        if self.floating_entry.winfo_viewable(): self.commit_edit(); self.hide_entry()
        
        cx = self.canvas.canvasx(event.x); cy = self.canvas.canvasy(event.y)
        row = int(cy // (ROW_HEIGHT + ROW_GAP))

        if row >= len(self.data): return

        col = -1; curr_x = FIXED_COL_0_WIDTH

        for i, w in enumerate(self.col_widths):
            if curr_x <= cx < curr_x + w: col = i; break
            curr_x += w
        
        is_ctrl = (event.state & 0x0004) or (event.state & 0x20000)
        
        if cx < FIXED_COL_0_WIDTH:

            if not is_ctrl: self.selected_rows.clear(); self.selected_cols.clear(); self.selected_cells.clear()
            if row in self.selected_rows: self.selected_rows.remove(row)
            else: self.selected_rows.add(row)

            self.redraw(); return

        if col != -1:

            if not is_ctrl:
                self.selected_rows.clear(); self.selected_cols.clear(); self.selected_cells.clear()
                self.show_editor(row, col)

            else:
                self.pre_drag_selection = self.selected_cells.copy()
                self.selected_cells.add((row, col))
                self.selection_anchor = (row, col)
                self.redraw()

    def on_drag(self, event):
        if not self.selection_anchor: return

        cx = self.canvas.canvasx(event.x); cy = self.canvas.canvasy(event.y)
        row = max(0, min(int(cy // (ROW_HEIGHT + ROW_GAP)), len(self.data)-1))
        
        col = -1; curr_x = FIXED_COL_0_WIDTH

        for i, w in enumerate(self.col_widths):
            if curr_x <= cx < curr_x + w: col = i; break

            curr_x += w

        if col == -1: return

        sr, sc = self.selection_anchor
        self.selected_cells = self.pre_drag_selection.copy()

        for r in range(min(sr, row), max(sr, row)+1):
            for c in range(min(sc, col), max(sc, col)+1):
                self.selected_cells.add((r, c))

        self.redraw()

    def show_editor(self, row, col, refresh=True):
        if self.editor_window_id: self.canvas.delete(self.editor_window_id)

        self.cur_row, self.cur_col = row, col
        self.entry_var.set(self.data[row][col])
        self.floating_entry.config(bg="#ffff99")
        self.redraw()
        
        x = FIXED_COL_0_WIDTH + sum(self.col_widths[:col]) + (GAP_WIDTH // 2)
        y = (row * (ROW_HEIGHT + ROW_GAP)) + 1
        w = self.col_widths[col] - GAP_WIDTH - 1
        
        self.editor_window_id = self.canvas.create_window(x+1, y+1, window=self.floating_entry, anchor='nw', width=w-1, height=ROW_HEIGHT-1)
        self.floating_entry.focus_set()
        self.floating_entry.icursor(tk.END)

        if refresh: self.app_manager.trigger_full_refresh()

    def hide_entry(self, event=None):
        if self.floating_entry.winfo_viewable():
            self.commit_edit()

            if self.editor_window_id: 
                self.canvas.delete(self.editor_window_id)
                self.editor_window_id = None

            self.redraw()

    def commit_edit(self):
        if not self.floating_entry.winfo_viewable(): return

        new_val = self.entry_var.get()

        if new_val != self.data[self.cur_row][self.cur_col] or (len(self.selected_cells) > 1 and (self.cur_row, self.cur_col) in self.selected_cells):
            self.history.record("Cell Edit")
            self.data[self.cur_row][self.cur_col] = new_val

            if len(self.selected_cells) > 1 and (self.cur_row, self.cur_col) in self.selected_cells:
                for (r, c) in self.selected_cells: self.data[r][c] = new_val

            self.app_manager.auto_save_trigger()

    def move_cursor(self, dr, dc):
        self.commit_edit()
        nr, nc = self.cur_row + dr, self.cur_col + dc

        if 0 <= nr < len(self.data) and 0 <= nc < len(self.headers):
            self.show_editor(nr, nc)

        return "break"
    
    def get_sheet_data(self): return self.data
    
    def update_name(self, name):
        self.sheet_name = name
        self.btn_print.config(text=f"Print Menu For: '{name}'")

    def get_completed_rows(self):
        rows = []
        ar, ac, live = -1, -1, ""

        if self.floating_entry.winfo_viewable(): ar, ac, live = self.cur_row, self.cur_col, self.entry_var.get()

        for i, r in enumerate(self.data):
            cr = list(r)
            if i == ar and 0 <= ac < len(cr): cr[ac] = live

            if len(cr)>4 and cr[1].strip() and cr[2].strip() and cr[3].strip() and cr[4].strip():
                try: rows.append({'row_idx': i, 'larousse': cr[1], 'bbd': cr[2], 'qty': cr[3], 'copies': int(cr[4])})
                except: pass

        return rows

    def jump_to_specific_cell(self, row, col, trigger_refresh=True):
        total_visible = self.canvas.winfo_height() or 600
        row_h = ROW_HEIGHT + ROW_GAP
        total_scroll = len(self.data) * row_h
        target_y = row * row_h
        desired = target_y - (total_visible/2) + (row_h/2)

        if total_scroll > 0: self.canvas.yview_moveto(max(0, min(1, desired/total_scroll)))
        
        self.show_editor(row, col, refresh=trigger_refresh)

    def on_body_scroll_x(self, f, l):
        self.h_scroll.set(f, l); self.header_canvas.xview_moveto(f)
        
    def _on_mousewheel(self, e):
        self.canvas.yview_scroll(int(-1*(e.delta/120)), "units")
        return "break"

    def on_generic_key_release(self, e):
        if e.keysym not in ("Return", "Tab", "Up", "Down", "Left", "Right", "Control_L", "Control_R"): 
            self.app_manager.trigger_full_refresh()

    def on_ctrl_release(self, e):
        if len(self.selected_cells) > 1:
            d = XPInputDialog(self.winfo_toplevel(), "Bulk", f"Set {len(self.selected_cells)} cells to:")

            if d.result is not None:
                self.history.record("Bulk Edit")
                self.app_manager.log_snapshot("Bulk Range Edit", target_sheet=self.sheet_name)

                for (r, c) in self.selected_cells: self.data[r][c] = d.result

                self.redraw(); self.app_manager.auto_save_trigger()

    def on_header_click(self, e):
        cx = e.x; curr = FIXED_COL_0_WIDTH

        for i, w in enumerate(self.col_widths):
            if curr <= cx < curr + w:
                self.selected_rows.clear()

                if i in self.selected_cols: self.selected_cols.remove(i)
                else: self.selected_cols.add(i)

                self.redraw(); return
            
            curr += w

    def delete_selection(self, e=None):
        if self.selected_cells:
            self.history.record("Clear Range")
            self.app_manager.log_snapshot("Cleared Range", target_sheet=self.sheet_name)

            for (r, c) in self.selected_cells: self.data[r][c] = ""

        elif self.selected_rows:
            rows = sorted(list(self.selected_rows), reverse=True)
            self.history.record(f"Deleted {len(rows)} Rows")
            self.app_manager.log_snapshot(f"Deleted {len(rows)} Rows", target_sheet=self.sheet_name)

            for r in rows: 
                self.data[r] = ["" for _ in self.headers]

            self.selected_rows.clear()

        elif self.selected_cols:
            cols = list(self.selected_cols)
            self.history.record("Deleted Columns")
            self.app_manager.log_snapshot("Deleted Columns", target_sheet=self.sheet_name)

            for c in cols:
                for row in self.data: row[c] = ""

            self.selected_cols.clear()
            
        self.redraw(); self.app_manager.auto_save_trigger()

    def open_print_manager(self):
        if PrintDialog:
            self.hide_entry()

            try: 
                self.wait_window(PrintDialog(self.winfo_toplevel(), self.app_manager, self.sheet_name))
            except: pass
            
        else: messagebox.showerror("Error", "Print_Manager missing.")
    
    def clear_row_data(self, idx):
        if 0 <= idx < len(self.data):
            self.data[idx][2] = ""; self.data[idx][3] = ""; self.data[idx][4] = ""
            self.redraw(); self.app_manager.auto_save_trigger()
    
    def refocus_cell(self):
        self.after(50, lambda: self.show_editor(self.cur_row, self.cur_col))