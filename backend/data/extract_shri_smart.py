"""
Script ekstraksi SHRI yang lebih robust
Designed specifically for RSJD Abepura format
"""

import pandas as pd
import os
import glob
from datetime import datetime
import sys

def extract_shri_data_smart(file_path: str, sheet_name: str, year: int, month: int) -> pd.DataFrame:
    """
    Extract SHRI data dengan pemahaman struktur khusus RSJD Abepura
    
    Format expected:
    - Row 0-1: Title
    - Row 2-4: Headers  
    - Row 5+: Data dengan kolom Tgl (1-31)
    """
    try:
        # Read dengan skip headers
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
        
        # Find data start row (biasanya setelah "Tgl" header)
        data_start_row = None
        for idx, row in df.iterrows():
            if any('tgl' in str(val).lower() for val in row if pd.notna(val)):
                data_start_row = idx + 2  # Skip 2 rows after header
                break
        
        if data_start_row is None:
            return pd.DataFrame()
        
        # Extract data rows
        data_rows = []
        
        for idx in range(data_start_row, len(df)):
            row = df.iloc[idx]
            
            # Column 0 should be day of month (1-31)
            try:
                day = int(float(row[0])) if pd.notna(row[0]) else None
                if day is None or day < 1 or day > 31:
                    continue
                
                # Construct full date
                tanggal = datetime(year, month, day).date()
                
                # Extract sensus data (adjust column indices based on inspection)
                pasien_awal = int(float(row[1])) if pd.notna(row[1]) and str(row[1]).replace('.','').isdigit() else 0
                pasien_masuk = int(float(row[2])) if pd.notna(row[2]) and str(row[2]).replace('.','').isdigit() else 0
                pasien_keluar_hidup = int(float(row[6])) if pd.notna(row[6]) and str(row[6]).replace('.','').isdigit() else 0
                pasien_akhir = int(float(row[14])) if pd.notna(row[14]) and str(row[14]).replace('.','').isdigit() else 0
                hari_rawat = int(float(row[18])) if pd.notna(row[18]) and str(row[18]).replace('.','').isdigit() else 0
                
                # Tempat tidur from header (try to find it)
                tempat_tidur = 20  # Default, will try to find from header
                
                # Calculate BOR
                if tempat_tidur > 0 and hari_rawat > 0:
                    bor = (hari_rawat / tempat_tidur) * 100
                else:
                    bor = 0.0
                
                # Validate BOR range
                if 0 < bor <= 200:
                    data_rows.append({
                        'tanggal': tanggal,
                        'pasien_awal': pasien_awal,
                        'masuk': pasien_masuk,
                        'keluar': pasien_keluar_hidup,
                        'pasien_akhir': pasien_akhir,
                        'tempat_tidur': tempat_tidur,
                        'hari_rawat': hari_rawat,
                        'bor': round(bor, 2)
                    })
                    
            except (ValueError, TypeError, IndexError) as e:
                continue
        
        return pd.DataFrame(data_rows)
        
    except Exception as e:
        print(f"    Error: {str(e)[:100]}")
        return pd.DataFrame()

def process_rekap_shri_files(sensus_folder: str):
    """Process all REKAP SHRI files"""
    
    print("\n" + "="*60)
    print("EXTRACTING SHRI DATA FROM REKAP FILES")
    print("="*60)
    
    all_data = []
    
    # Find all REKAP SHRI folders
    rekap_folders = [
        "REKAP SHRI 2020",
        "REKAP SHRI 2021", 
        "REKAP SHRI 2022"
    ]
    
    for folder_name in rekap_folders:
        folder_path = os.path.join(sensus_folder, folder_name)
        
        if not os.path.exists(folder_path):
            print(f"\nFolder not found: {folder_name}")
            continue
        
        print(f"\n{'='*60}")
        print(f"Processing: {folder_name}")
        print(f"{'='*60}")
        
        # Extract year from folder name
        year = int(folder_name.split()[-1])
        
        # Find all Excel files in this folder
        excel_files = glob.glob(os.path.join(folder_path, "*.xlsx"))
        
        for file_path in excel_files:
            # Skip temp files
            if os.path.basename(file_path).startswith('~$'):
                continue
            
            print(f"\n  File: {os.path.basename(file_path)}")
            
            try:
                xls = pd.ExcelFile(file_path)
                
                # Map sheet names to months
                month_map = {
                    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
                    "mei": 5, "jun": 6, "jul": 7, "agus": 8, "agust": 8,
                    "sept": 9, "sep": 9, "okt": 10, "nov": 11, "des": 12
                }
                
                for sheet_name in xls.sheet_names:
                    # Extract month from sheet name
                    sheet_lower = sheet_name.lower().replace("'", "")
                    month = None
                    
                    for month_name, month_num in month_map.items():
                        if month_name in sheet_lower:
                            month = month_num
                            break
                    
                    if month is None:
                        continue
                    
                    print(f"    Sheet: {sheet_name} -> {year}-{month:02d}", end=" ... ")
                    
                    df = extract_shri_data_smart(file_path, sheet_name, year, month)
                    
                    if not df.empty:
                        all_data.append(df)
                        print(f"OK ({len(df)} records)")
                    else:
                        print("No data")
                        
            except Exception as e:
                print(f"    ERROR: {str(e)[:100]}")
                continue
    
    if not all_data:
        print("\n\nERROR: No data extracted!")
        return None
    
    # Combine all data
    print(f"\n{'='*60}")
    print("COMBINING DATA")
    print(f"{'='*60}")
    
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Sort by date
    combined_df = combined_df.sort_values('tanggal')
    
    # Remove duplicates
    original_count = len(combined_df)
    combined_df = combined_df.drop_duplicates(subset=['tanggal'], keep='first')
    duplicates = original_count - len(combined_df)
    
    # Filter valid BOR
    original_count = len(combined_df)
    combined_df = combined_df[
        (combined_df['bor'] > 0) & 
        (combined_df['bor'] <= 100)
    ]
    outliers = original_count - len(combined_df)
    
    print(f"\nTotal records: {len(combined_df)}")
    print(f"Duplicates removed: {duplicates}")
    print(f"Outliers removed: {outliers}")
    print(f"\nDate range: {combined_df['tanggal'].min()} to {combined_df['tanggal'].max()}")
    print(f"BOR range: {combined_df['bor'].min():.1f}% to {combined_df['bor'].max():.1f}%")
    print(f"BOR mean: {combined_df['bor'].mean():.1f}%")
    print(f"BOR median: {combined_df['bor'].median():.1f}%")
    
    return combined_df

def main():
    sensus_folder = r"c:\Users\Ryn\Desktop\Jurnal\TA_sensus\SENSUS"
    output_csv = r"c:\Users\Ryn\Desktop\Jurnal\TA_sensus\data\shri_training_data.csv"
    
    if not os.path.exists(sensus_folder):
        print(f"ERROR: Folder not found: {sensus_folder}")
        return 1
    
    # Extract data
    df = process_rekap_shri_files(sensus_folder)
    
    if df is None or len(df) < 30:
        print("\n\nERROR: Insufficient data extracted (need at least 30 days)")
        return 1
    
    # Save to CSV
    print(f"\n{'='*60}")
    print("SAVING DATA")
    print(f"{'='*60}")
    
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False, encoding='utf-8')
    
    print(f"\nCSV saved: {output_csv}")
    print(f"Records: {len(df)}")
    
    # Show sample
    print(f"\nSample data:")
    print(df.head(10).to_string(index=False))
    
    print(f"\n{'='*60}")
    print("SUCCESS!")
    print(f"{'='*60}")
    print(f"\nData siap untuk training SARIMA model!")
    print(f"\nNext steps:")
    print(f"  1. Train model: cd backend && python models/train_sarima.py")
    print(f"  2. Test API: python test_prediksi_api.py")
    
    return 0

if __name__ == "__main__":
    exit(main())
