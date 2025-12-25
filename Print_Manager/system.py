import win32print

def get_system_printers():
    try:
        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
        names = [p[2] for p in printers]
        return names if names else ["No Printers Found"]
    except: return ["No Printers Found"]

def get_default_printer():
    try: return win32print.GetDefaultPrinter()
    except: return ""