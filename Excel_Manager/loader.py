import pandas as pd
from tkinter import filedialog, messagebox

class ExcelLoader:
    def prompt_file(self, root):
        return filedialog.askopenfilename(
            parent=root,
            title="Select Inventory Excel File",
            filetypes=[("Excel Files", "*.xlsx;*.xls")]
        )

    def load_raw_dataframe(self, file_path):
        try:
            return pd.read_excel(file_path, sheet_name="Packing List", header=None)
        except ValueError:
            raise ValueError("Sheet 'Packing List' not found.")
        except Exception as e:
            raise Exception(f"Read failed: {e}")