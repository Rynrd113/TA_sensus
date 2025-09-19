# Bangsal Management System - Technical Documentation

## System Architecture

### Model Relationships
```
Bangsal (1) ─── (N) KamarBangsal
   │
   ├── capacity calculations
   ├── occupancy rates  
   ├── emergency status
   └── statistics aggregation
```

### Database Schema

#### Bangsal Table
```sql
CREATE TABLE bangsal (
    id INTEGER PRIMARY KEY,
    nama_bangsal VARCHAR(100) NOT NULL,
    kode_bangsal VARCHAR(20) UNIQUE NOT NULL,
    kapasitas_total INTEGER NOT NULL DEFAULT 0,
    jumlah_kamar INTEGER NOT NULL DEFAULT 0,
    tempat_tidur_tersedia INTEGER NOT NULL DEFAULT 0,
    tempat_tidur_terisi INTEGER NOT NULL DEFAULT 0,
    departemen VARCHAR(100),
    jenis_bangsal VARCHAR(50) NOT NULL,
    kategori VARCHAR(50),
    lantai INTEGER,
    gedung VARCHAR(100),
    lokasi_detail TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_emergency_ready BOOLEAN DEFAULT FALSE,
    kepala_bangsal VARCHAR(100),
    perawat_jaga VARCHAR(100),
    dokter_penanggung_jawab VARCHAR(100),
    tarif_per_hari FLOAT DEFAULT 0.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_by INTEGER,
    fasilitas TEXT,
    keterangan TEXT
);
```

#### KamarBangsal Table
```sql
CREATE TABLE kamar_bangsal (
    id INTEGER PRIMARY KEY,
    nomor_kamar VARCHAR(20) NOT NULL,
    nama_kamar VARCHAR(100),
    kapasitas_kamar INTEGER NOT NULL DEFAULT 1,
    tempat_tidur_terisi INTEGER NOT NULL DEFAULT 0,
    jenis_kamar VARCHAR(50),
    fasilitas_kamar TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_maintenance BOOLEAN DEFAULT FALSE,
    status_kebersihan VARCHAR(20) DEFAULT 'Bersih',
    bangsal_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bangsal_id) REFERENCES bangsal(id)
);
```

### Key Features

#### 1. Real-time Occupancy Calculation
```python
@property
def occupancy_rate(self) -> float:
    """Calculate current occupancy rate (BOR for this bangsal)"""
    if self.kapasitas_total == 0:
        return 0.0
    return (self.tempat_tidur_terisi / self.kapasitas_total) * 100
```

#### 2. Emergency Readiness Status
- Tracks which bangsal are prepared for emergency admissions
- Filters available beds for emergency use
- Provides quick access for emergency department

#### 3. Capacity Synchronization
```python
def update_capacity_from_rooms(self):
    """Update total capacity based on rooms"""
    total_capacity = sum(room.kapasitas_kamar for room in self.kamar_list if room.is_active)
    total_occupied = sum(room.tempat_tidur_terisi for room in self.kamar_list if room.is_active)
    
    self.kapasitas_total = total_capacity
    self.tempat_tidur_terisi = total_occupied
    self.tempat_tidur_tersedia = total_capacity - total_occupied
```

#### 4. Advanced Query Capabilities
- Department-based filtering
- Emergency readiness filtering  
- Occupancy rate ranges
- Available bed thresholds
- Full-text search across multiple fields

#### 5. Role-Based Access Control
- **Viewer**: Read-only access to bangsal information
- **Nurse**: Can update bed occupancy and basic info
- **Doctor**: Can create/update bangsal, manage rooms
- **Admin**: Full access including deletion and validation

### Integration Points

#### 1. Sensus Harian Integration
The bangsal system integrates with the existing sensus system:
- Provides real-time bed availability for patient admissions
- Updates occupancy automatically from patient movements  
- Supports BOR calculations at bangsal level

#### 2. Dashboard Integration
- Real-time occupancy widgets
- Department performance metrics
- Emergency bed availability alerts
- Trend analysis and forecasting

#### 3. Reporting Integration
- Daily census reports per bangsal
- Monthly occupancy statistics
- Department performance analysis
- Capacity planning reports

### Performance Considerations

#### 1. Database Indexing
```sql
CREATE INDEX idx_bangsal_kode ON bangsal(kode_bangsal);
CREATE INDEX idx_bangsal_active ON bangsal(is_active);
CREATE INDEX idx_bangsal_emergency ON bangsal(is_emergency_ready);
CREATE INDEX idx_bangsal_department ON bangsal(departemen);
CREATE INDEX idx_kamar_bangsal_id ON kamar_bangsal(bangsal_id);
```

#### 2. Caching Strategy
- Cache frequently accessed statistics
- Cache department listings
- Cache emergency-ready bangsal list
- Invalidate cache on capacity updates

#### 3. Async Operations
All service methods are async-enabled for better scalability:
```python
async def get_bangsal_list(self, page: int = 1, per_page: int = 20) -> BangsalList:
    """Async method for non-blocking operations"""
```

### Security Considerations

#### 1. Input Validation
- Strict validation on all numeric fields
- JSON format validation for facilities
- Capacity constraints enforcement
- Unique code validation

#### 2. Access Control
- JWT token validation on all endpoints
- Role-based endpoint restrictions
- User activity logging
- Audit trail for all modifications

#### 3. Data Integrity
- Foreign key constraints
- Check constraints for capacity ranges
- Soft delete for data preservation
- Transaction rollback on errors

### Monitoring and Alerting

#### 1. Key Metrics
- Overall hospital occupancy rate
- Per-department occupancy rates
- Emergency bed availability
- Capacity utilization trends

#### 2. Alert Conditions
- Occupancy rate > 90%
- Emergency beds < 5
- Bangsal capacity mismatches
- Extended high occupancy periods

#### 3. Health Checks
```python
def validate_bangsal_data(self, bangsal_data: BangsalCreate) -> List[str]:
    """Validate bangsal data and return list of errors"""
    errors = []
    
    if bangsal_data.kapasitas_total < 0:
        errors.append("Kapasitas total tidak boleh negatif")
    
    # Additional validation checks...
    return errors
```

### Deployment Considerations

#### 1. Environment Configuration
- Database connection pooling
- Redis cache configuration
- JWT secret management
- CORS policy settings

#### 2. Scaling
- Horizontal scaling with load balancer
- Database connection pooling
- Cache layer for frequent queries
- Background tasks for statistics

#### 3. Backup and Recovery
- Daily database backups
- Transaction log backups
- Point-in-time recovery capability
- Disaster recovery procedures

### Testing Strategy

#### 1. Unit Tests
- Model validation tests
- Service layer business logic tests
- Repository query tests
- Schema validation tests

#### 2. Integration Tests  
- API endpoint tests
- Database transaction tests
- Authentication flow tests
- Role permission tests

#### 3. Load Testing
- Concurrent user simulation
- Database performance under load
- API response time benchmarks
- Memory usage profiling

### Future Enhancements

#### 1. Analytics Dashboard
- Occupancy trend visualization
- Predictive analytics for capacity planning
- Department performance comparison
- Real-time alerts and notifications

#### 2. Mobile Application
- Mobile-friendly API endpoints
- Push notifications for critical alerts
- Offline capability for basic operations
- QR code scanning for room identification

#### 3. Integration Expansions
- Electronic Health Records (EHR) integration
- Patient admission workflow integration
- Housekeeping status management
- Maintenance scheduling system

### Troubleshooting Guide

#### 1. Common Issues
- **Capacity Mismatch**: Use validate endpoint to identify inconsistencies
- **Import Errors**: Check relative import paths in router files
- **Authentication Failures**: Verify JWT token expiration and format
- **Permission Denied**: Check user roles and endpoint requirements

#### 2. Debug Commands
```bash
# Check database connectivity
python3 validate_bangsal_system.py

# Test API endpoints
curl -X GET http://localhost:8000/api/v1/bangsal/statistics/occupancy

# Validate specific bangsal
curl -X POST http://localhost:8000/api/v1/bangsal/1/validate
```

#### 3. Log Analysis
- Check application logs in `/backend/logs/app.log`
- Monitor database query performance
- Track API response times
- Review authentication failures