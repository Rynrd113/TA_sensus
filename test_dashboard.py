#!/usr/bin/env python3
import sys
import os
sys.path.append('/home/rynrd/Documents/Project/TA/sensus-rs/sensus-rs')

from backend.database.session import get_db
from backend.services.dashboard_service import get_dashboard_stats

def test_dashboard_service():
    # Get database session
    db = next(get_db())
    
    try:
        # Test dashboard service
        result = get_dashboard_stats(db, bulan=7, tahun=2025)
        print("Dashboard Service Result:")
        print(result)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_dashboard_service()
