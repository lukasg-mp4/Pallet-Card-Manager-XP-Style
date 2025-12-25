import win32print
import win32ui
import win32con

class GDIPrinter:
    def send_page(self, item):
        try:
            printer = win32print.GetDefaultPrinter()
            hDC = win32ui.CreateDC()
            hDC.CreatePrinterDC(printer)
            hDC.StartDoc(f"Label {item['larousse']}")
            hDC.StartPage()
            
            pw = hDC.GetDeviceCaps(win32con.HORZRES)
            ph = hDC.GetDeviceCaps(win32con.VERTRES)
            max_w = int(pw * 0.9)

            def get_h(text, target):
                curr = target; limit = int(target * 0.2)
                while abs(curr) > abs(limit):
                    dc = win32ui.CreateDCFromHandle(hDC.GetHandleAttrib())
                    font = win32ui.CreateFont({'name':'Tahoma', 'height':curr, 'weight':700})
                    old = dc.SelectObject(font)
                    w = dc.GetTextExtent(text)[0]
                    dc.SelectObject(old)
                    if w <= max_w: return curr
                    curr = int(curr * 0.9)
                return curr

            def text_out(txt, y_pct, h_target):
                fh = get_h(txt, int(-1 * (pw * h_target)))
                font = win32ui.CreateFont({'name':'Tahoma', 'height':fh, 'weight':700})
                old = hDC.SelectObject(font)
                sz = hDC.GetTextExtent(txt)
                x = (pw - sz[0]) // 2
                y = int(ph * y_pct) - (sz[1] // 2)
                hDC.TextOut(x, y, txt)
                hDC.SelectObject(old)

            text_out(item['larousse'], 0.20, 0.28)
            text_out(item['bbd'], 0.50, 0.26)
            text_out(f"X {item['qty']}", 0.80, 0.28)
            
            hDC.EndPage(); hDC.EndDoc(); hDC.DeleteDC()
            return True
        except: return False