import sys
import os
import tkinter as tk
import getpass
import datetime
import hashlib as _sys_core
import ctypes # --- NEW IMPORT ---

# --- IMPORT NEW MODULES ---
from UI.XP_Styling.assets import XP_SHADOW_OFFSETS
from UI.XP_Styling.license_view import LicenseAgreement
from UI.Main_Layout.Main.app import InventoryApp 

# --- NEW: Win32 Setup for Taskbar Grouping ---
try:
    myappid = 'tetis.inventory.manager.v1' 
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

if __name__ == "__main__":
    _ui_cache_path = "license.key"
    
    # Pull data from assets
    _render_id = "".join([chr(c) for c in XP_SHADOW_OFFSETS])
    
    _system_ready = False

    def _validate_resource_integrity():
        if not os.path.exists(_ui_cache_path):
            return False
            
        try:
            with open(_ui_cache_path, "r") as f:
                _buffer = f.readlines()
                
            if len(_buffer) < 3: return False 
            
            _header_u = _buffer[0].strip()
            _ts_init = _buffer[1].strip()
            _stored_token = _buffer[2].strip()
            
            _data_stream = f"{_header_u}|{_ts_init}|{_render_id}"
            _computed_token = _sys_core.sha256(_data_stream.encode()).hexdigest()
            
            if _computed_token == _stored_token:
                return True 
            else:
                return False 
        except:
            return False

    # 1. Perform Integrity Check
    if _validate_resource_integrity():
        _system_ready = True
    else:
        # Create temp root for EULA
        _t_root = tk.Tk()
        _t_root.withdraw()
        
        dlg = LicenseAgreement(_t_root)
        
        if dlg.result:
            try:
                _curr_usr = getpass.getuser()
                _curr_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                _stream_out = f"{_curr_usr}|{_curr_ts}|{_render_id}"
                _session_token = _sys_core.sha256(_stream_out.encode()).hexdigest()
                
                with open(_ui_cache_path, "w") as f:
                    f.write(f"{_curr_usr}\n")
                    f.write(f"{_curr_ts}\n")
                    f.write(f"{_session_token}")
                    
                _system_ready = True
            except Exception as e:
                tk.messagebox.showerror("System Error", f"Write Error 0x1: {e}")
                _system_ready = False 
        else:
            _system_ready = False
        
        _t_root.destroy()

    # 2. Launch App
    if _system_ready:
        root = tk.Tk()
        app = InventoryApp(root) 
        root.mainloop()
    else:
        sys.exit()