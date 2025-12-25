import pandas as pd
import datetime

class DataProcessor:
    def process(self, df):
        # 1. Find Header
        header_idx, col_map = self._find_headers(df)
        if header_idx == -1:
            raise ValueError("Could not find header row (Customer Code, Qty/Box).")

        # 2. Extract Rows
        return self._extract_rows(df, header_idx, col_map)

    def _find_headers(self, df):
        targets = {
            "Larousse": ["Customer Code", "CustomerCode"],
            "BBD": ["Best by Date", "Best By", "Shelf Life"], 
            "Qty": ["Qty/Box"]
        }
        
        for idx, row in df.iterrows():
            vals = [str(v).strip().lower() for v in row.values]
            if any("customer code" in v for v in vals) and any("qty/box" in v for v in vals):
                col_map = {}
                for c_idx, val in enumerate(row.values):
                    s = str(val).strip()
                    if any(t in s for t in targets["Larousse"]): col_map["Larousse"] = c_idx
                    elif any(t in s for t in targets["BBD"]): col_map["BBD"] = c_idx
                    elif any(t in s for t in targets["Qty"]): col_map["Qty"] = c_idx
                
                if len(col_map) >= 2:
                    return idx, col_map
        return -1, {}

    def _extract_rows(self, df, header_idx, col_map):
        rows = []
        for _, row in df.iloc[header_idx+1:].iterrows():
            try:
                l_val = row.iloc[col_map.get("Larousse")] if "Larousse" in col_map else None
                if pd.isna(l_val) or str(l_val).strip() == "": continue
                if "total" in str(l_val).lower(): break

                q_val = row.iloc[col_map.get("Qty")] if "Qty" in col_map else ""
                if pd.isna(q_val): q_val = ""
                
                b_val = row.iloc[col_map.get("BBD")] if "BBD" in col_map else ""
                b_str = self._format_date(b_val)

                rows.append({
                    "Larousse": str(l_val).strip(),
                    "BBD": b_str,
                    "Qty": str(int(float(q_val))) if str(q_val).replace('.', '', 1).isdigit() else str(q_val)
                })
            except: continue
        return rows

    def _format_date(self, val):
        if pd.isna(val): return ""
        if isinstance(val, datetime.datetime):
            return val.strftime("%d.%m.%y")
        try:
            return pd.to_datetime(str(val).strip()).strftime("%d.%m.%y")
        except:
            return str(val).strip().replace('-', '.').replace('/', '.')