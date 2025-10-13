#!/usr/bin/env python3
"""
SAMPLE DATA GENERATION FOR JOURNAL PUBLICATION
===============================================

Script untuk generate data sintetis realistis rumah sakit periode 2023-2024 (730 hari)
Sesuai dengan karakteristik SHRI (Sistem Informasi Rumah Sakit) Indonesia.

KOMPONEN DATA SINTETIS:
- Trend: Pertumbuhan 2-3% per tahun
- Weekly seasonality: Senin-Jumat tinggi, Weekend turun 20%
- Monthly seasonality: Akhir bulan naik 10%
- Random noise: ±5%
- Seasonal spikes: Simulasi musim flu dan penyakit seasonal
- Range realistis: 40-90% BOR (target optimal 60-85% sesuai Kemenkes)

Author: Research Team
Date: October 2025
Purpose: Jurnal publikasi SARIMA forecasting
"""

import sys
import os
from datetime import date, timedelta, datetime
from typing import List, Tuple, Dict
import random
import math
import json
import csv
import numpy as np
import pandas as pd

# Add backend path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# Change to backend directory for correct database access
os.chdir(backend_dir)

from database.session import SessionLocal
from models.sensus import SensusHarian, Base
from database.engine import engine

# Set random seed untuk reproducible results
random.seed(42)
np.random.seed(42)

class RealisticSampelDataGenerator:
    """
    Generator data sintetis realistis untuk penelitian SARIMA rumah sakit
    
    Karakteristik yang disimulasikan:
    1. Growth trend tahunan 2-3%
    2. Weekly seasonality (weekday vs weekend)
    3. Monthly seasonality (end of month effect)
    4. Seasonal disease patterns (flu season, holiday effects)
    5. Random noise yang masuk akal
    6. Compliance dengan standar Kemenkes (BOR 60-85%)
    """
    
    def __init__(self):
        # Hospital parameters (RS Type B - 200 bed capacity)
        self.base_capacity = 200
        self.capacity_growth_rate = 0.02  # 2% growth per year
        
        # BOR targets sesuai Kemenkes
        self.target_bor_min = 60.0  # Minimum yang direkomendasikan
        self.target_bor_max = 85.0  # Maximum yang direkomendasikan
        self.target_bor_optimal = 72.5  # Target optimal (rata-rata)
        
        # Seasonal patterns
        self.monthly_factors = {
            1: 1.15,   # Januari - tinggi (post holiday, flu season)
            2: 1.20,   # Februari - peak flu season
            3: 1.10,   # Maret - masih tinggi (flu season ending)
            4: 1.05,   # April - normal+ (allergy season)
            5: 1.00,   # Mei - normal
            6: 0.95,   # Juni - sedikit turun (liburan sekolah)
            7: 0.90,   # Juli - turun (peak holiday)
            8: 0.92,   # Agustus - sedikit naik
            9: 1.00,   # September - kembali normal
            10: 1.08,  # Oktober - naik (post holiday, start of rainy season)
            11: 1.12,  # November - tinggi (rainy season diseases)
            12: 1.25   # Desember - tertinggi (holiday stress, year-end)
        }
        
        # Weekly patterns
        self.weekday_factors = {
            0: 1.10,  # Monday - tinggi (weekend emergency backlog)
            1: 1.05,  # Tuesday - normal+
            2: 1.00,  # Wednesday - normal
            3: 1.02,  # Thursday - sedikit tinggi
            4: 0.98,  # Friday - sedikit turun
            5: 0.80,  # Saturday - turun signifikan
            6: 0.75   # Sunday - terendah
        }
        
        # Special event factors
        self.holiday_periods = [
            # Format: (start_month, start_day, end_month, end_day, factor)
            (12, 20, 1, 7, 0.85),    # Christmas/New Year period
            (6, 15, 7, 31, 0.88),    # School holiday mid-year
            (3, 15, 3, 25, 1.15),    # Flu season peak
            (8, 15, 8, 20, 0.92),    # Independence Day period
        ]
        
        # Disease outbreak simulation
        self.outbreak_probability = 0.05  # 5% chance per month
        self.outbreak_duration_days = (7, 21)  # 1-3 weeks
        self.outbreak_intensity = (1.3, 1.8)   # 30-80% increase
        
    def get_capacity_for_date(self, date_obj: date) -> int:
        """Calculate capacity dengan growth trend"""
        # Base capacity dengan growth
        years_from_start = (date_obj - date(2023, 1, 1)).days / 365.25
        growth_factor = (1 + self.capacity_growth_rate) ** years_from_start
        
        base_capacity = int(self.base_capacity * growth_factor)
        
        # Add small random variation (±5%)
        variation = random.uniform(-0.05, 0.05)
        adjusted_capacity = int(base_capacity * (1 + variation))
        
        # Ensure reasonable bounds
        return max(180, min(220, adjusted_capacity))
    
    def get_seasonal_factor(self, date_obj: date) -> float:
        """Calculate combined seasonal factor"""
        # Monthly seasonality
        monthly_factor = self.monthly_factors.get(date_obj.month, 1.0)
        
        # Weekly seasonality
        weekly_factor = self.weekday_factors.get(date_obj.weekday(), 1.0)
        
        # End of month effect (last 3 days of month)
        eom_factor = 1.0
        if date_obj.day >= 28:  # Last few days of month
            # Calculate days until end of month
            next_month = date_obj.replace(day=28) + timedelta(days=4)
            end_of_month = next_month - timedelta(days=next_month.day)
            days_to_eom = (end_of_month - date_obj).days
            if days_to_eom <= 2:
                eom_factor = 1.10  # 10% increase end of month
        
        # Holiday effects
        holiday_factor = 1.0
        for start_m, start_d, end_m, end_d, factor in self.holiday_periods:
            if self.is_in_period(date_obj, start_m, start_d, end_m, end_d):
                holiday_factor = factor
                break
        
        return monthly_factor * weekly_factor * eom_factor * holiday_factor
    
    def is_in_period(self, date_obj: date, start_m: int, start_d: int, 
                     end_m: int, end_d: int) -> bool:
        """Check if date is in specified period"""
        start_date = date(date_obj.year, start_m, start_d)
        
        if end_m < start_m:  # Cross year boundary
            end_date = date(date_obj.year + 1, end_m, end_d)
        else:
            end_date = date(date_obj.year, end_m, end_d)
        
        return start_date <= date_obj <= end_date
    
    def simulate_disease_outbreak(self, date_obj: date, outbreak_schedule: Dict) -> float:
        """Simulate random disease outbreaks"""
        date_str = date_obj.strftime('%Y-%m-%d')
        
        if date_str in outbreak_schedule:
            days_into_outbreak = outbreak_schedule[date_str]['days_into']
            intensity = outbreak_schedule[date_str]['intensity']
            duration = outbreak_schedule[date_str]['duration']
            
            # Outbreak pattern: ramp up, peak, ramp down
            if days_into_outbreak <= duration * 0.3:  # Ramp up
                factor = 1.0 + (intensity - 1.0) * (days_into_outbreak / (duration * 0.3))
            elif days_into_outbreak <= duration * 0.7:  # Peak
                factor = intensity
            else:  # Ramp down
                remaining_days = duration - days_into_outbreak
                ramp_down_period = duration * 0.3
                factor = 1.0 + (intensity - 1.0) * (remaining_days / ramp_down_period)
            
            return factor
        
        return 1.0
    
    def generate_outbreak_schedule(self, start_date: date, end_date: date) -> Dict:
        """Generate random disease outbreak schedule"""
        outbreak_schedule = {}
        current_date = start_date
        
        while current_date <= end_date:
            # Check for outbreak start (5% chance per month, only on 1st)
            if current_date.day == 1 and random.random() < self.outbreak_probability:
                duration = random.randint(*self.outbreak_duration_days)
                intensity = random.uniform(*self.outbreak_intensity)
                
                # Schedule outbreak days
                for i in range(duration):
                    outbreak_date = current_date + timedelta(days=i)
                    if outbreak_date <= end_date:
                        outbreak_schedule[outbreak_date.strftime('%Y-%m-%d')] = {
                            'days_into': i,
                            'duration': duration,
                            'intensity': intensity
                        }
            
            current_date += timedelta(days=1)
        
        return outbreak_schedule
    
    def calculate_target_bor(self, date_obj: date, outbreak_schedule: Dict) -> float:
        """Calculate target BOR untuk tanggal tertentu"""
        # Base BOR target
        base_bor = self.target_bor_optimal
        
        # Apply seasonal factors
        seasonal_factor = self.get_seasonal_factor(date_obj)
        outbreak_factor = self.simulate_disease_outbreak(date_obj, outbreak_schedule)
        
        # Calculate target BOR
        target_bor = base_bor * seasonal_factor * outbreak_factor
        
        # Add trend (slight increase over time due to population growth)
        years_from_start = (date_obj - date(2023, 1, 1)).days / 365.25
        trend_factor = 1 + (0.01 * years_from_start)  # 1% increase per year
        target_bor *= trend_factor
        
        # Add random noise (±5%)
        noise = random.uniform(-0.05, 0.05)
        target_bor *= (1 + noise)
        
        # Ensure bounds (40-90% as specified)
        return max(40.0, min(90.0, target_bor))
    
    def calculate_patient_flow(self, date_obj: date, capacity: int, 
                              target_bor: float, prev_patients: int) -> Tuple[int, int, int]:
        """
        Calculate realistic patient flow berdasarkan target BOR
        Returns: (pasien_awal, masuk, keluar)
        """
        target_patients = int(capacity * (target_bor / 100))
        
        # Pasien awal = previous day's end patients (dengan adjustment)
        if prev_patients is None:
            # First day - estimate based on target
            pasien_awal = int(target_patients * random.uniform(0.85, 1.15))
        else:
            pasien_awal = prev_patients
        
        # Calculate admission (new patients)
        # Base admission rate: 8-15% of capacity per day
        base_admission_rate = random.uniform(0.08, 0.15)
        seasonal_factor = self.get_seasonal_factor(date_obj)
        
        expected_masuk = int(capacity * base_admission_rate * seasonal_factor)
        
        # Add variation
        variation = random.normalvariate(0, expected_masuk * 0.2)
        masuk = max(0, int(expected_masuk + variation))
        
        # Ensure we don't exceed capacity
        max_masuk = capacity - pasien_awal
        masuk = min(masuk, max_masuk)
        
        # Calculate discharge to reach target
        total_patients = pasien_awal + masuk
        
        # Target discharge to reach desired BOR
        target_keluar = total_patients - target_patients
        
        # Add realistic constraints (average LOS 4-7 days)
        avg_los = random.uniform(4.0, 7.0)
        max_keluar_by_los = int(total_patients / avg_los * 1.5)  # Allow some flexibility
        
        # Final discharge calculation
        keluar = max(0, min(target_keluar, max_keluar_by_los, total_patients))
        
        # Add small random variation
        variation = random.normalvariate(0, max(1, keluar * 0.1))
        keluar = max(0, min(int(keluar + variation), total_patients))
        
        return pasien_awal, masuk, keluar
    
    def calculate_hari_rawat(self, pasien_awal: int, masuk: int, keluar: int) -> int:
        """Calculate hari rawat realistis"""
        # Hari rawat = patient days
        # Approximation: patients at start + new admissions - 0.5 * discharges
        # (assuming discharges happen on average mid-day)
        patient_days = pasien_awal + masuk - (keluar * 0.5)
        return max(0, int(patient_days))
    
    def calculate_indicators(self, pasien_awal: int, masuk: int, keluar: int, 
                           capacity: int, hari_rawat: int) -> Tuple[float, float, float, float]:
        """Calculate all hospital indicators"""
        pasien_akhir = pasien_awal + masuk - keluar
        
        # BOR - Bed Occupancy Rate
        bor = round((pasien_akhir / capacity) * 100, 2) if capacity > 0 else 0.0
        
        # LOS - Length of Stay (average)
        los = round(hari_rawat / keluar, 2) if keluar > 0 else 0.0
        
        # BTO - Bed Turnover
        bto = round(keluar / capacity, 3) if capacity > 0 else 0.0
        
        # TOI - Turn Over Interval
        empty_beds = max(0, capacity - pasien_akhir)
        toi = round(empty_beds / keluar, 2) if keluar > 0 else 0.0
        
        return bor, los, bto, toi
    
    def generate_sample_data(self, start_date: date, end_date: date) -> List[Dict]:
        """
        Generate comprehensive realistic sample data
        """
        print(f"🎲 Generating realistic sample data: {start_date} to {end_date}")
        
        total_days = (end_date - start_date).days + 1
        print(f"📊 Total days to generate: {total_days}")
        
        # Generate outbreak schedule
        print("🦠 Generating disease outbreak schedule...")
        outbreak_schedule = self.generate_outbreak_schedule(start_date, end_date)
        outbreak_count = len(set(v['duration'] for v in outbreak_schedule.values()))
        print(f"📈 Generated {outbreak_count} disease outbreaks over the period")
        
        data_list = []
        current_date = start_date
        prev_patients = None
        
        progress_step = max(1, total_days // 20)  # Show progress every 5%
        
        while current_date <= end_date:
            # Show progress
            days_done = (current_date - start_date).days
            if days_done % progress_step == 0:
                progress = (days_done / total_days) * 100
                print(f"⏳ Progress: {progress:.1f}% ({current_date})")
            
            # Calculate parameters for this date
            capacity = self.get_capacity_for_date(current_date)
            target_bor = self.calculate_target_bor(current_date, outbreak_schedule)
            
            pasien_awal, masuk, keluar = self.calculate_patient_flow(
                current_date, capacity, target_bor, prev_patients
            )
            
            hari_rawat = self.calculate_hari_rawat(pasien_awal, masuk, keluar)
            bor, los, bto, toi = self.calculate_indicators(
                pasien_awal, masuk, keluar, capacity, hari_rawat
            )
            
            # Create data record
            data_record = {
                'tanggal': current_date.strftime('%Y-%m-%d'),
                'jml_pasien_awal': pasien_awal,
                'jml_masuk': masuk,
                'jml_keluar': keluar,
                'jml_pasien_akhir': pasien_awal + masuk - keluar,
                'tempat_tidur_tersedia': capacity,
                'hari_rawat': hari_rawat,
                'bor': bor,
                'los': los,
                'bto': bto,
                'toi': toi
            }
            
            data_list.append(data_record)
            
            # Update for next iteration
            prev_patients = data_record['jml_pasien_akhir']
            current_date += timedelta(days=1)
        
        print(f"✅ Generated {len(data_list)} records successfully!")
        return data_list
    
    def validate_generated_data(self, data_list: List[Dict]) -> Dict:
        """Validate generated data quality"""
        print("\n🔍 VALIDATING GENERATED DATA...")
        
        df = pd.DataFrame(data_list)
        
        validation_results = {
            'total_records': len(data_list),
            'date_range': {
                'start': df['tanggal'].min(),
                'end': df['tanggal'].max()
            },
            'bor_statistics': {
                'min': float(df['bor'].min()),
                'max': float(df['bor'].max()),
                'mean': float(df['bor'].mean()),
                'median': float(df['bor'].median()),
                'std': float(df['bor'].std())
            },
            'capacity_statistics': {
                'min': int(df['tempat_tidur_tersedia'].min()),
                'max': int(df['tempat_tidur_tersedia'].max()),
                'mean': float(df['tempat_tidur_tersedia'].mean())
            },
            'data_quality': {
                'bor_in_range_40_90': ((df['bor'] >= 40) & (df['bor'] <= 90)).mean() * 100,
                'bor_optimal_60_85': ((df['bor'] >= 60) & (df['bor'] <= 85)).mean() * 100,
                'los_reasonable_2_15': ((df['los'] >= 2) & (df['los'] <= 15)).mean() * 100
            }
        }
        
        # Print validation summary
        print(f"📊 Total records: {validation_results['total_records']}")
        print(f"📅 Date range: {validation_results['date_range']['start']} to {validation_results['date_range']['end']}")
        print(f"🏥 BOR range: {validation_results['bor_statistics']['min']:.1f}% - {validation_results['bor_statistics']['max']:.1f}%")
        print(f"🎯 BOR mean: {validation_results['bor_statistics']['mean']:.1f}% (target: 72.5%)")
        print(f"✅ BOR in valid range (40-90%): {validation_results['data_quality']['bor_in_range_40_90']:.1f}%")
        print(f"🎯 BOR in optimal range (60-85%): {validation_results['data_quality']['bor_optimal_60_85']:.1f}%")
        print(f"🛏️ Capacity range: {validation_results['capacity_statistics']['min']} - {validation_results['capacity_statistics']['max']} beds")
        
        return validation_results

def save_to_csv(data_list: List[Dict], filepath: str):
    """Save data to CSV file"""
    print(f"💾 Saving to CSV: {filepath}")
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        if data_list:
            fieldnames = data_list[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(data_list)
    
    print(f"✅ CSV saved: {len(data_list)} records")

def save_to_sqlite(data_list: List[Dict], db_session):
    """Save data to SQLite database"""
    print("💾 Saving to SQLite database...")
    
    # Drop and recreate table to ensure correct schema
    print("🔄 Recreating database schema...")
    try:
        # Drop all tables and recreate
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("✅ Database schema recreated")
    except Exception as e:
        print(f"⚠️ Schema recreation warning: {e}")
    
    # Insert new data in batches
    batch_size = 100
    total = len(data_list)
    
    for i in range(0, total, batch_size):
        batch = data_list[i:i + batch_size]
        
        sensus_objects = []
        for item in batch:
            sensus_obj = SensusHarian(
                tanggal=datetime.strptime(item['tanggal'], '%Y-%m-%d').date(),
                jml_pasien_awal=item['jml_pasien_awal'],
                jml_masuk=item['jml_masuk'],
                jml_keluar=item['jml_keluar'],
                jml_pasien_akhir=item['jml_pasien_akhir'],
                tempat_tidur_tersedia=item['tempat_tidur_tersedia'],
                hari_rawat=item['hari_rawat'],
                bor=item['bor'],
                los=item['los'],
                bto=item['bto'],
                toi=item['toi']
            )
            sensus_objects.append(sensus_obj)
        
        db_session.add_all(sensus_objects)
        db_session.commit()
        
        progress = min(i + batch_size, total)
        print(f"📊 SQLite Progress: {progress}/{total} ({(progress/total)*100:.1f}%)")
    
    print(f"✅ SQLite saved: {total} records")

def save_documentation(validation_results: Dict, filepath: str):
    """Save data generation documentation"""
    print(f"📝 Creating documentation: {filepath}")
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    doc_content = f"""# Data Generation Notes - SARIMA Research

## Overview
Data sintetis yang dibangkitkan untuk penelitian SARIMA forecasting rumah sakit.

**Periode**: {validation_results['date_range']['start']} sampai {validation_results['date_range']['end']}  
**Total Records**: {validation_results['total_records']} hari  
**Hospital Type**: RS Type B (200 bed capacity)

## Karakteristik Data Sintetis

### 1. Trend Components
- **Growth Rate**: 2% per tahun (capacity expansion)
- **Population Growth Effect**: 1% per tahun (demand increase)
- **BOR Target**: 72.5% (optimal sesuai standar Kemenkes)

### 2. Seasonal Patterns

#### Monthly Seasonality
- **Januari-Februari**: Peak flu season (+15-20%)
- **Juni-Agustus**: Holiday season (-5-10%)
- **Oktober-Desember**: Rainy season diseases (+8-25%)

#### Weekly Seasonality
- **Senin**: Tertinggi (+10% - weekend emergency backlog)
- **Selasa-Kamis**: Normal (±5%)
- **Jumat**: Sedikit turun (-2%)
- **Weekend**: Turun signifikan (-20-25%)

#### End-of-Month Effect
- **3 hari terakhir bulan**: Naik 10% (administrative patient processing)

### 3. Disease Outbreak Simulation
- **Probability**: 5% per bulan
- **Duration**: 1-3 minggu
- **Intensity**: 30-80% increase in admissions
- **Pattern**: Ramp up → Peak → Ramp down

### 4. Random Components
- **BOR Noise**: ±5% random variation
- **Capacity Variation**: ±5% from base capacity
- **Patient Flow Noise**: Normally distributed around expected values

## Data Quality Validation

### BOR (Bed Occupancy Rate)
- **Range**: {validation_results['bor_statistics']['min']:.1f}% - {validation_results['bor_statistics']['max']:.1f}%
- **Mean**: {validation_results['bor_statistics']['mean']:.1f}%
- **Standard Deviation**: {validation_results['bor_statistics']['std']:.1f}%
- **Valid Range (40-90%)**: {validation_results['data_quality']['bor_in_range_40_90']:.1f}%
- **Optimal Range (60-85%)**: {validation_results['data_quality']['bor_optimal_60_85']:.1f}%

### Capacity
- **Range**: {validation_results['capacity_statistics']['min']} - {validation_results['capacity_statistics']['max']} beds
- **Average**: {validation_results['capacity_statistics']['mean']:.0f} beds

### Length of Stay (LOS)
- **Reasonable Range (2-15 days)**: {validation_results['data_quality']['los_reasonable_2_15']:.1f}%

## Compliance dengan Standar Kemenkes

✅ **BOR Target**: 60-85% (optimal range compliance: {validation_results['data_quality']['bor_optimal_60_85']:.1f}%)  
✅ **Data Range**: 40-90% (requirement compliance: {validation_results['data_quality']['bor_in_range_40_90']:.1f}%)  
✅ **Realistic Patterns**: Weekly, monthly, seasonal variations included  
✅ **Hospital Indicators**: BOR, LOS, BTO, TOI calculated according to standard formulas

## Journal Methodology Statement

**Suggested text for journal:**

> "Data yang digunakan merupakan data sintetis yang dibangkitkan dengan karakteristik realistis berdasarkan pola SHRI rumah sakit pada umumnya. Data mencakup {validation_results['total_records']} observasi harian periode {validation_results['date_range']['start']} sampai {validation_results['date_range']['end']}, dengan komponen trend tahunan (2-3%), seasonality mingguan dan bulanan, variasi end-of-month, simulasi outbreak penyakit seasonal, dan noise acak (±5%). Range BOR berada dalam standar Kemenkes 40-90% dengan target optimal 60-85%, mencapai compliance rate {validation_results['data_quality']['bor_optimal_60_85']:.1f}%."

## Files Generated

1. **sample_shri_data.csv** - Raw data dalam format CSV
2. **SQLite Database** - Data tersimpan dalam tabel sensus_harian
3. **data_generation_notes.md** - Dokumentasi ini

## Reproducibility

- **Random Seed**: 42 (fixed untuk reproducible results)
- **Algorithm**: Deterministic dengan probabilistic components
- **Parameters**: Documented dalam source code

---
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
Generator: RealisticSampelDataGenerator v1.0  
Purpose: SARIMA Research Journal Publication
"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(doc_content)
    
    print(f"✅ Documentation saved")

def main():
    """Main function untuk generate sample data"""
    print("🏥 SAMPLE DATA GENERATION FOR JOURNAL PUBLICATION")
    print("=" * 65)
    print("📊 Target: 730 hari (2023-2024) data sintetis realistis")
    print("🎯 Purpose: Penelitian SARIMA forecasting rumah sakit")
    print("📝 Compliance: Standar Kemenkes BOR 40-90% (optimal 60-85%)")
    print()
    
    # Setup
    start_date = date(2023, 1, 1)
    end_date = date(2024, 12, 31)
    total_days = (end_date - start_date).days + 1
    
    print(f"📅 Periode: {start_date} sampai {end_date}")
    print(f"📊 Total hari: {total_days}")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Initialize generator
    generator = RealisticSampelDataGenerator()
    
    try:
        # Generate data
        print(f"\n🎲 GENERATING REALISTIC SAMPLE DATA")
        print("-" * 40)
        data_list = generator.generate_sample_data(start_date, end_date)
        
        # Validate data quality
        print(f"\n🔍 VALIDATING DATA QUALITY")
        print("-" * 40)
        validation_results = generator.validate_generated_data(data_list)
        
        # Save to files
        print(f"\n💾 SAVING TO FILES")
        print("-" * 40)
        
        # Paths
        project_root = os.path.dirname(os.path.dirname(backend_dir))
        csv_path = os.path.join(project_root, "data", "sample_shri_data.csv")
        doc_path = os.path.join(project_root, "data", "data_generation_notes.md")
        
        # Save CSV
        save_to_csv(data_list, csv_path)
        
        # Save to SQLite
        db = SessionLocal()
        try:
            save_to_sqlite(data_list, db)
        finally:
            db.close()
        
        # Save documentation
        save_documentation(validation_results, doc_path)
        
        # Final summary
        print(f"\n🎉 SUCCESS! SAMPLE DATA GENERATION COMPLETED")
        print("=" * 65)
        print(f"📊 Generated: {len(data_list)} records ({total_days} days)")
        print(f"📁 CSV File: {csv_path}")
        print(f"📄 Documentation: {doc_path}")
        print(f"🗄️ SQLite: Updated with new data")
        print(f"🎯 BOR Quality: {validation_results['data_quality']['bor_optimal_60_85']:.1f}% in optimal range")
        print()
        print("✅ Data siap untuk penelitian SARIMA!")
        print("📚 Gunakan dokumentasi untuk metodologi jurnal")
        
        # Test compatibility warning
        print(f"\n⚠️  NEXT STEPS:")
        print("1. Test compatibility dengan model training pipeline")
        print("2. Run SARIMA training dengan data baru")
        print("3. Validasi performa model dengan dataset yang lebih besar")
        print("4. Update jurnal dengan metodologi data generation")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())