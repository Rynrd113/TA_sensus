#!/usr/bin/env python3
"""
Script untuk ekstrak data SHRI dari Excel ke CSV format training
Data riil dari RSJ 2020-2022
"""

import pandas as pd
import os
from datetime import datetime
import glob
import sys

def find_excel_files(base_path: str) -> list:
    """Find all Excel files in SENSUS folders"""
    excel_files = []
    
    # Search patterns
    patterns = [
        "**/*.xlsx",
        "**/*.xls"
    ]
    
    for pattern in patterns:
        files = glob.glob(os.path.join(base_path, pattern), recursive=True)
        excel_files.extend(files)
    
    return excel_files

def extract_sensus_data(file_path: str) -> pd.DataFrame:
    """
    Extract sensus data from Excel file
    Adaptable untuk berbagai format Excel SHRI
    """
    print(f"\n📂 Processing: {os.path.basename(file_path)}")
    
    try:
        # Try reading Excel dengan berbagai sheet
        xls = pd.ExcelFile(file_path)
        
        all_data = []
        
        for sheet_name in xls.sheet_names:
            print(f"  📄 Sheet: {sheet_name}")
            
            try:
                # Try reading with different header rows
                df = None
                for header_row in [0, 1, 2, 3, 4]:
                    try:
                        df_temp = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)
                        # Check if we found data row with 'Tgl' or 'Tanggal' column
                        cols_str = [str(col).lower() for col in df_temp.columns]
                        if any('tgl' in col or 'tanggal' in col or 'date' in col for col in cols_str):
                            df = df_temp
                            break
                    except:
                        continue
                
                if df is None:
                    # Last resort: read without header and find the row
                    df_temp = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
                    for idx, row in df_temp.iterrows():
                        row_str = ' '.join([str(x).lower() for x in row if pd.notna(x)])
                        if 'tgl' in row_str or 'tanggal' in row_str:
                            df = pd.read_excel(file_path, sheet_name=sheet_name, header=idx)
                            break
                
                if df is None:
                    print(f"    ⚠️ Could not find data structure, skipping")
                    continue
                
                # Skip empty sheets
                if df.empty or len(df) < 5:
                    print(f"    ⚠️ Sheet empty or too small, skipping")
                    continue
                
                # Remove rows that are all NaN
                df = df.dropna(how='all')
                
                # Normalisasi nama kolom
                df.columns = df.columns.astype(str).str.lower().str.strip()
                
                # Cari kolom tanggal (berbagai kemungkinan nama)
                date_cols = [col for col in df.columns if any(
                    keyword in str(col).lower() for keyword in ['tanggal', 'tgl', 'date', 'hari']
                )]
                
                if not date_cols:
                    print(f"    ⚠️ No date column found, skipping sheet")
                    continue
                
                date_col = date_cols[0]
                
                # Cari kolom data sensus
                sensus_mapping = {
                    'tanggal': date_col,
                    'pasien_awal': None,
                    'masuk': None,
                    'keluar': None,
                    'pasien_akhir': None,
                    'tempat_tidur': None,
                    'hari_rawat': None,
                    'bor': None
                }
                
                # Map kolom-kolom sensus
                for col in df.columns:
                    col_lower = str(col).lower()
                    if 'awal' in col_lower or 'sisa' in col_lower:
                        sensus_mapping['pasien_awal'] = col
                    elif 'masuk' in col_lower or 'in' in col_lower:
                        sensus_mapping['masuk'] = col
                    elif 'keluar' in col_lower or 'out' in col_lower or 'pulang' in col_lower:
                        sensus_mapping['keluar'] = col
                    elif 'akhir' in col_lower:
                        sensus_mapping['pasien_akhir'] = col
                    elif 'tempat tidur' in col_lower or 'tt' in col_lower or 'bed' in col_lower:
                        sensus_mapping['tempat_tidur'] = col
                    elif 'hari rawat' in col_lower or 'hp' in col_lower or 'lama' in col_lower:
                        sensus_mapping['hari_rawat'] = col
                    elif 'bor' in col_lower or 'occupancy' in col_lower:
                        sensus_mapping['bor'] = col
                
                # Buat dataframe bersih
                clean_data = []
                
                for idx, row in df.iterrows():
                    try:
                        # Parse tanggal
                        tanggal = pd.to_datetime(row[date_col], errors='coerce')
                        
                        if pd.isna(tanggal):
                            continue
                        
                        # Extract data dengan error handling
                        def safe_int(val, default=0):
                            try:
                                return int(float(val)) if not pd.isna(val) else default
                            except:
                                return default
                        
                        def safe_float(val, default=0.0):
                            try:
                                return float(val) if not pd.isna(val) else default
                            except:
                                return default
                        
                        # Extract data
                        data_row = {
                            'tanggal': tanggal.date(),
                            'pasien_awal': safe_int(row.get(sensus_mapping['pasien_awal'], 0)),
                            'masuk': safe_int(row.get(sensus_mapping['masuk'], 0)),
                            'keluar': safe_int(row.get(sensus_mapping['keluar'], 0)),
                            'pasien_akhir': safe_int(row.get(sensus_mapping['pasien_akhir'], 0)),
                            'tempat_tidur': safe_int(row.get(sensus_mapping['tempat_tidur'], 100), 100),
                            'hari_rawat': safe_int(row.get(sensus_mapping['hari_rawat'], 0)),
                        }
                        
                        # Calculate BOR jika tidak ada
                        if sensus_mapping['bor'] and not pd.isna(row.get(sensus_mapping['bor'])):
                            data_row['bor'] = safe_float(row[sensus_mapping['bor']])
                        else:
                            # Calculate BOR
                            if data_row['tempat_tidur'] > 0 and data_row['hari_rawat'] > 0:
                                data_row['bor'] = (data_row['hari_rawat'] / data_row['tempat_tidur']) * 100
                            else:
                                data_row['bor'] = 0.0
                        
                        # Validate data
                        if 0 < data_row['bor'] <= 200:  # Reasonable range
                            clean_data.append(data_row)
                        
                    except Exception as e:
                        continue  # Skip invalid rows
                
                if clean_data:
                    sheet_df = pd.DataFrame(clean_data)
                    all_data.append(sheet_df)
                    print(f"    ✅ Extracted {len(clean_data)} valid records")
                
            except Exception as e:
                print(f"    ❌ Error reading sheet: {str(e)}")
                continue
        
        # Combine all sheets
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            return combined_df
        else:
            return pd.DataFrame()
            
    except Exception as e:
        print(f"  ❌ Error processing file: {str(e)}")
        return pd.DataFrame()

def process_all_shri_files(sensus_folder: str, output_csv: str):
    """
    Process all SHRI Excel files and combine into single CSV
    """
    print("🏥 EXTRACTING SHRI DATA FROM EXCEL TO CSV")
    print("=" * 60)
    
    # Find all Excel files
    print(f"\n🔍 Searching for Excel files in: {sensus_folder}")
    excel_files = find_excel_files(sensus_folder)
    
    print(f"📊 Found {len(excel_files)} Excel files:")
    for f in excel_files[:5]:  # Show first 5
        print(f"   - {os.path.basename(f)}")
    if len(excel_files) > 5:
        print(f"   ... and {len(excel_files) - 5} more files")
    
    if not excel_files:
        print("❌ No Excel files found!")
        return False
    
    # Process each file
    all_dataframes = []
    
    for file_path in excel_files:
        df = extract_sensus_data(file_path)
        if not df.empty:
            all_dataframes.append(df)
    
    if not all_dataframes:
        print("\n❌ No data extracted from any file!")
        return False
    
    # Combine all data
    print("\n📊 COMBINING ALL DATA")
    print("-" * 60)
    
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    
    # Sort by date
    combined_df = combined_df.sort_values('tanggal')
    
    # Remove duplicates (same date)
    original_count = len(combined_df)
    combined_df = combined_df.drop_duplicates(subset=['tanggal'], keep='first')
    duplicates_removed = original_count - len(combined_df)
    
    if duplicates_removed > 0:
        print(f"🗑️ Removed {duplicates_removed} duplicate dates")
    
    # Filter valid BOR range (0-100%)
    original_count = len(combined_df)
    combined_df = combined_df[
        (combined_df['bor'] >= 0) & 
        (combined_df['bor'] <= 100)
    ]
    outliers_removed = original_count - len(combined_df)
    
    if outliers_removed > 0:
        print(f"🗑️ Removed {outliers_removed} outliers (BOR >100% or <0%)")
    
    print(f"\n✅ Total valid records: {len(combined_df)}")
    print(f"📅 Date range: {combined_df['tanggal'].min()} to {combined_df['tanggal'].max()}")
    print(f"📊 BOR statistics:")
    print(f"   - Min: {combined_df['bor'].min():.1f}%")
    print(f"   - Max: {combined_df['bor'].max():.1f}%")
    print(f"   - Mean: {combined_df['bor'].mean():.1f}%")
    print(f"   - Median: {combined_df['bor'].median():.1f}%")
    print(f"   - Std Dev: {combined_df['bor'].std():.1f}%")
    
    # Save to CSV
    print(f"\n💾 Saving to: {output_csv}")
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    
    combined_df.to_csv(output_csv, index=False, encoding='utf-8')
    
    print(f"✅ CSV saved successfully! ({len(combined_df)} records)")
    
    # Show sample data
    print(f"\n📋 Sample data (first 5 rows):")
    print(combined_df.head().to_string(index=False))
    
    # Also save to SQLite
    print(f"\n💾 Saving to SQLite database...")
    save_to_sqlite(combined_df)
    
    return True

def save_to_sqlite(df: pd.DataFrame):
    """Save extracted data to SQLite database"""
    try:
        # Add parent directory to path
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        from database.session import SessionLocal
        from models.sensus import SensusHarian, Base
        from database.engine import engine
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        
        db = SessionLocal()
        try:
            # Clear existing data
            print("🗑️  Clearing existing data from database...")
            existing_count = db.query(SensusHarian).count()
            db.query(SensusHarian).delete()
            db.commit()
            print(f"   Removed {existing_count} old records")
            
            # Insert new data
            print("💾 Inserting new data to database...")
            
            for idx, row in df.iterrows():
                sensus = SensusHarian(
                    tanggal=row['tanggal'],
                    jml_pasien_awal=row['pasien_awal'],
                    jml_masuk=row['masuk'],
                    jml_keluar=row['keluar'],
                    jml_pasien_akhir=row['pasien_akhir'],
                    tempat_tidur_tersedia=row['tempat_tidur'],
                    hari_rawat=row['hari_rawat'],
                    bor=row['bor'],
                    jml_dirawat=row['pasien_awal'] + row['masuk']
                )
                db.add(sensus)
                
                if (idx + 1) % 100 == 0:
                    db.commit()
                    print(f"   ✅ Saved {idx + 1}/{len(df)} records...")
            
            db.commit()
            print(f"✅ All {len(df)} records saved to database!")
            
        except Exception as e:
            print(f"❌ Error saving to database: {str(e)}")
            db.rollback()
        finally:
            db.close()
            
    except ImportError as e:
        print(f"⚠️  Could not save to database: {str(e)}")
        print("   CSV file is still available for manual import")

def main():
    """Main execution"""
    # Path configuration
    sensus_folder = r"c:\Users\Ryn\Desktop\Jurnal\TA_sensus\SENSUS"
    output_csv = r"c:\Users\Ryn\Desktop\Jurnal\TA_sensus\data\shri_training_data.csv"
    
    # Check if SENSUS folder exists
    if not os.path.exists(sensus_folder):
        print(f"❌ SENSUS folder not found: {sensus_folder}")
        return 1
    
    # Process files
    success = process_all_shri_files(sensus_folder, output_csv)
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 EXTRACTION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"📁 Output CSV: {output_csv}")
        print(f"🗄️  SQLite Database: Updated")
        print("\n✅ Data siap untuk training SARIMA!")
        print("\n📝 Next steps:")
        print("   1. Verify data: python -c 'import pandas as pd; df=pd.read_csv(\"data/shri_training_data.csv\"); print(df.info())'")
        print("   2. Train model: python backend/models/train_sarima.py")
        print("   3. Test prediction: python backend/test_prediksi_api.py")
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ EXTRACTION FAILED!")
        print("=" * 60)
        print("Check the error messages above and try again.")
        return 1

if __name__ == "__main__":
    exit(main())
