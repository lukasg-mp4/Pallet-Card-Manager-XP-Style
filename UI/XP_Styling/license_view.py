import tkinter as tk
from .colors import XP_BORDER_COLOR, XP_BEIGE, XP_BTN_BG
from .fonts import XP_FONT_BOLD, XP_FONT
from .title_bar import XPTitleBar

class LicenseAgreement(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.result = False
        self.withdraw(); self.configure(bg=XP_BORDER_COLOR); self.overrideredirect(True)
        w, h = 750, 500
        x = (self.winfo_screenwidth() // 2) - (w // 2); y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        main_frame = tk.Frame(self, bg=XP_BORDER_COLOR, bd=3); main_frame.pack(fill=tk.BOTH, expand=True)
        self.title_bar = XPTitleBar(main_frame, self, title_text="License Agreement")
        self.title_bar.btn_close.config(state="disabled", command=lambda: None) 
        content = tk.Frame(main_frame, bg=XP_BEIGE, padx=15, pady=15); content.pack(fill=tk.BOTH, expand=True)

        tk.Label(content, 
                 text="Please read the following license agreement carefully.", 
                 bg=XP_BEIGE, 
                 font=("Tahoma", 10, "bold")).pack(anchor="w", pady=(0, 10))
        
        text_frame = tk.Frame(content, bd=2, relief="sunken", bg="white"); text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        scrollbar = tk.Scrollbar(text_frame); scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area = tk.Text(text_frame, wrap="word", font=("Tahoma", 9), bg="white", bd=0, highlightthickness=0, yscrollcommand=scrollbar.set, padx=10, pady=10)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_area.yview)

        self.insert_legal_text()
        self.text_area.config(state="disabled") 
        btn_frame = tk.Frame(content, bg=XP_BEIGE); btn_frame.pack(fill=tk.X)
        tk.Button(btn_frame, text="I Accept", width=15, command=self.accept, bg=XP_BTN_BG, relief="raised", bd=2, font=XP_FONT_BOLD).pack(side=tk.RIGHT, padx=10)
        tk.Button(btn_frame, text="Decline", width=15, command=self.decline, bg=XP_BTN_BG, relief="raised", bd=2, font=XP_FONT).pack(side=tk.RIGHT, padx=10)
        self.deiconify(); self.lift(); self.focus_force(); self.grab_set(); self.wait_window(self)

    def insert_legal_text(self):
        legal_text = """END USER LICENSE AGREEMENT (EULA)

1. OWNERSHIP

This software application ("Pallet Card Manager") is the intellectual property of Lukas Geciauskas. It is NOT property 
of the business entity where it is installed. The business is granted a license to use the Software, but ownership 
remains strictly with the Author.

2. LICENSE GRANT

The Author grants you a revocable, non-exclusive, non-transferable, limited license to download, install, and use the 
Software solely for your internal business purposes strictly in accordance with the terms of this Agreement.

3. RESTRICTIONS
You agree not to, and you will not permit others to:

a) License, sell, rent, lease, assign, distribute, transmit, host, outsource, disclose, or commercially exploit the Software.
b) Modify, make derivative works of, disassemble, decrypt, reverse compile, or reverse engineer any part of the Software.
c) Remove, alter, or obscure any proprietary notice (including any notice of copyright or trademark) of the Author.

4. DISCLAIMER OF WARRANTY

The Software is provided "AS IS", without warranty of any kind, express or implied. The Author shall not be liable 
for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or 
in connection with the Software or the use or other dealings in the Software.

5. TERMINATION

This Agreement is effective until terminated. Your rights under this Agreement will terminate automatically without 
notice from the Author if you fail to comply with any term(s) of this Agreement. Upon termination of the 
Agreement, you shall cease all use of the Software and destroy all copies, full or partial, of the Software.

Copyright (c) 2025 Lukas Geciauskas. All rights reserved."""

        self.text_area.insert("1.0", legal_text)

    def accept(self):
        self.result = True; self.destroy()

    def decline(self):
        self.result = False; self.destroy()