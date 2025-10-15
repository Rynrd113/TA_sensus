"""
Script untuk inspect struktur Excel SHRI dan test ekstraksi
"""
import pandas as pd
import os

# Test one file
file_path = r"c:\Users\Ryn\Desktop\Jurnal\TA_sensus\SENSUS\REKAP SHRI 2020\Rekapitulasi Sensus Harian R.Akut.xlsx"

print("="*60)
print("INSPECTING EXCEL STRUCTURE")
print("="*60)

xls = pd.ExcelFile(file_path)
print(f"\nFile: {os.path.basename(file_path)}")
print(f"Sheets: {xls.sheet_names}")

# Check first sheet
sheet_name = xls.sheet_names[0]
print(f"\n\nAnalyzing sheet: {sheet_name}")
print("-"*60)

# Try different header rows
for header_row in range(10):
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)
        print(f"\nHEADER ROW {header_row}:")
        print(f"  Columns: {list(df.columns[:10])}")
        print(f"  Shape: {df.shape}")
        
        # Check for date column
        cols_str = [str(col).lower() for col in df.columns]
        date_cols = [col for col in df.columns if any(kw in str(col).lower() for kw in ['tgl', 'tanggal', 'date', 'hari'])]
        
        if date_cols:
            print(f"  Date columns found: {date_cols}")
            print(f"\n  First 10 rows of data:")
            print(df.head(10).to_string())
            print(f"\n  Data types:")
            print(df.dtypes.head(10))
            break
    except Exception as e:
        print(f"\nHEADER ROW {header_row}: Error - {str(e)[:100]}")
