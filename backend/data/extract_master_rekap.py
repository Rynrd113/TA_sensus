"""
Script untuk extract data dari file MASTER REKAP INDIKATOR
File: DATA REKAP INDIKATOR TAHUN 2020-....xlsx
Sheets: 2020, 2021, 2022
"""

import pandas as pd
import os
from datetime import datetime

def extract_from_master_file():
    """Extract data dari file master"""
    
    master_file = r"c:\Users\Ryn\Desktop\Jurnal\TA_sensus\SENSUS\DATA REKAP INDIKATOR TAHUN 2020-....xlsx"
    output_csv = r"c:\Users\Ryn\Desktop\Jurnal\TA_sensus\data\shri_training_data.csv"
    
    print("=" * 70)
    print("EXTRACTING DATA FROM MASTER REKAP FILE")
    print("=" * 70)
    print(f"\nFile: {os.path.basename(master_file)}")
    
    # Read Excel file
    xls = pd.ExcelFile(master_file)
    print(f"Sheets found: {xls.sheet_names}")
    
    all_data = []
    
    for sheet_name in xls.sheet_names:
        if sheet_name not in ['2020', '2021', '2022']:
            continue
            
        print(f"\n{'='*50}")
        print(f"Processing Sheet: {sheet_name}")
        print(f"{'='*50}")
        
        # Read sheet - try different header rows
        df = pd.read_excel(master_file, sheet_name=sheet_name)
        
        print(f"Shape: {df.shape}")
        print(f"Columns (first 10): {df.columns.tolist()[:10]}")
        
        # Find date columns by looking for consecutive dates in first few rows
        # Biasanya tanggal ada di row tertentu
        for start_row in range(10):
            df_temp = pd.read_excel(master_file, sheet_name=sheet_name, header=start_row)
            
            # Check if first column contains dates
            try:
                # Try to convert first column to datetime
                if 'Unnamed' in str(df_temp.columns[0]) or 'TGL' in str(df_temp.columns[0]).upper():
                    # Try converting first row
                    test_val = df_temp.iloc[0, 0]
                    if pd.notna(test_val):
                        try:
                            test_date = pd.to_datetime(test_val)
                            print(f"\nFound date structure at row {start_row}")
                            print(f"First date: {test_date}")
                            
                            # This looks like the right row
                            # Now extract the data
                            extracted = extract_sheet_data(df_temp, sheet_name)
                            if len(extracted) > 0:
                                all_data.extend(extracted)
                                break
                        except:
                            pass
            except:
                pass
    
    if not all_data:
        print("\n[ERROR] No data extracted!")
        return False
    
    # Create DataFrame
    df_combined = pd.DataFrame(all_data)
    
    # Sort by date
    df_combined = df_combined.sort_values('tanggal')
    
    # Remove duplicates
    original_len = len(df_combined)
    df_combined = df_combined.drop_duplicates(subset=['tanggal'], keep='first')
    print(f"\n{'='*70}")
    print(f"Removed {original_len - len(df_combined)} duplicate dates")
    
    # Statistics
    print(f"\n{'='*70}")
    print(f"FINAL DATASET STATISTICS")
    print(f"{'='*70}")
    print(f"Total records: {len(df_combined)}")
    print(f"Date range: {df_combined['tanggal'].min()} to {df_combined['tanggal'].max()}")
    print(f"\nBOR Statistics:")
    print(f"  Min: {df_combined['bor'].min():.2f}%")
    print(f"  Max: {df_combined['bor'].max():.2f}%")
    print(f"  Mean: {df_combined['bor'].mean():.2f}%")
    print(f"  Median: {df_combined['bor'].median():.2f}%")
    print(f"  Std: {df_combined['bor'].std():.2f}%")
    
    # Save
    print(f"\nSaving to: {output_csv}")
    df_combined.to_csv(output_csv, index=False)
    print(f"[SUCCESS] CSV saved!")
    
    # Preview
    print(f"\nFirst 10 records:")
    print(df_combined.head(10))
    
    print(f"\nLast 10 records:")
    print(df_combined.tail(10))
    
    return True

def extract_sheet_data(df, year):
    """Extract data from a sheet"""
    data = []
    
    # Assume first column is date
    date_col = df.columns[0]
    
    # Find BOR column (usually has 'BOR' or '%' in name)
    bor_col = None
    for col in df.columns:
        if 'BOR' in str(col).upper() or '%' in str(col):
            bor_col = col
            break
    
    if bor_col is None:
        # Try to find numeric columns that might be BOR
        # BOR usually between 0-100
        for col in df.columns:
            try:
                vals = pd.to_numeric(df[col], errors='coerce')
                if vals.notna().any():
                    if (vals[vals.notna()] >= 0).all() and (vals[vals.notna()] <= 150).all():
                        # This might be BOR
                        avg_val = vals.mean()
                        if 0 < avg_val < 100:
                            bor_col = col
                            print(f"  Found potential BOR column: {col} (avg: {avg_val:.2f})")
                            break
            except:
                pass
    
    if bor_col is None:
        print(f"  [WARNING] Could not find BOR column in sheet {year}")
        return data
    
    print(f"  Date column: {date_col}")
    print(f"  BOR column: {bor_col}")
    
    # Extract data row by row
    for idx, row in df.iterrows():
        try:
            # Parse date
            date_val = row[date_col]
            if pd.isna(date_val):
                continue
                
            tanggal = pd.to_datetime(date_val, errors='coerce')
            if pd.isna(tanggal):
                continue
            
            # Parse BOR
            bor_val = row[bor_col]
            if pd.isna(bor_val):
                continue
            
            bor = float(bor_val)
            
            # Validate BOR range
            if bor < 0 or bor > 150:
                continue
            
            data.append({
                'tanggal': tanggal.date(),
                'pasien_awal': 0,  # Not available in master file
                'masuk': 0,
                'keluar': 0,
                'pasien_akhir': 0,
                'tempat_tidur': 100,  # Assumed
                'hari_rawat': int(bor) if bor > 0 else 0,  # Approximate
                'bor': bor
            })
            
        except Exception as e:
            continue
    
    print(f"  Extracted {len(data)} records from {year}")
    return data

if __name__ == "__main__":
    success = extract_from_master_file()
    if success:
        print("\n" + "="*70)
        print("[SUCCESS] Data extraction completed!")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("[FAILED] Data extraction failed!")
        print("="*70)
