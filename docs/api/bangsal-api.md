# Bangsal Management API Documentation

## Overview
Sistem manajemen bangsal (hospital ward management) menyediakan API lengkap untuk mengelola bangsal rumah sakit, kamar, kapasitas tempat tidur, dan statistik okupansi.

## Authentication
Semua endpoint memerlukan autentikasi JWT Bearer token, kecuali yang disebutkan khusus.

### Login untuk mendapatkan token:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": 1,
    "username": "admin",
    "roles": ["admin"]
  }
}
```

## Base URL
```
http://localhost:8000/api/v1/bangsal
```

## Endpoints

### 1. Create Bangsal
Membuat bangsal baru.

**Endpoint:** `POST /bangsal`  
**Role Required:** Admin, Doctor

```bash
curl -X POST http://localhost:8000/api/v1/bangsal \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nama_bangsal": "Bangsal Dahlia",
    "kode_bangsal": "DH-001",
    "kapasitas_total": 24,
    "jumlah_kamar": 6,
    "departemen": "Internal Medicine",
    "jenis_bangsal": "Kelas I",
    "kategori": "Rawat Inap",
    "lantai": 2,
    "gedung": "Gedung Utama",
    "lokasi_detail": "Lantai 2, Sayap Utara",
    "is_active": true,
    "is_emergency_ready": false,
    "kepala_bangsal": "Dr. Sari Wulandari",
    "perawat_jaga": "Ns. Budi Santoso",
    "dokter_penanggung_jawab": "Dr. Ahmad Fauzi",
    "tarif_per_hari": 450000.0,
    "fasilitas": "{\"AC\": true, \"TV\": true, \"WiFi\": true}",
    "keterangan": "Bangsal kelas I dengan fasilitas lengkap"
  }'
```

**Response:** `201 Created`
```json
{
  "id": 7,
  "nama_bangsal": "Bangsal Dahlia",
  "kode_bangsal": "DH-001",
  "kapasitas_total": 24,
  "jumlah_kamar": 6,
  "tempat_tidur_tersedia": 24,
  "tempat_tidur_terisi": 0,
  "occupancy_rate": 0.0,
  "available_beds": 24,
  "departemen": "Internal Medicine",
  "jenis_bangsal": "Kelas I",
  "is_active": true,
  "is_emergency_ready": false,
  "created_at": "2025-09-19T05:30:00",
  "updated_at": "2025-09-19T05:30:00"
}
```

### 2. Get All Bangsal
Mendapatkan daftar semua bangsal dengan pagination dan filter.

**Endpoint:** `GET /bangsal`  
**Role Required:** Any authenticated user

```bash
# Basic request
curl -X GET "http://localhost:8000/api/v1/bangsal" \
  -H "Authorization: Bearer YOUR_TOKEN"

# With pagination
curl -X GET "http://localhost:8000/api/v1/bangsal?page=1&per_page=10" \
  -H "Authorization: Bearer YOUR_TOKEN"

# With filters
curl -X GET "http://localhost:8000/api/v1/bangsal?jenis_bangsal=ICU&is_emergency_ready=true" \
  -H "Authorization: Bearer YOUR_TOKEN"

# With search
curl -X GET "http://localhost:8000/api/v1/bangsal?search=ICU" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:** `200 OK`
```json
{
  "total": 6,
  "page": 1,
  "per_page": 10,
  "pages": 1,
  "bangsal": [
    {
      "id": 1,
      "nama_bangsal": "Bangsal Mawar",
      "kode_bangsal": "MW-001",
      "kapasitas_total": 20,
      "tempat_tidur_tersedia": 15,
      "tempat_tidur_terisi": 5,
      "occupancy_rate": 25.0,
      "departemen": "Internal Medicine",
      "jenis_bangsal": "Kelas I",
      "is_active": true,
      "is_emergency_ready": false
    }
  ]
}
```

### 3. Get Bangsal by ID
Mendapatkan detail bangsal berdasarkan ID.

**Endpoint:** `GET /bangsal/{bangsal_id}`  
**Role Required:** Any authenticated user

```bash
curl -X GET "http://localhost:8000/api/v1/bangsal/1" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Include room details
curl -X GET "http://localhost:8000/api/v1/bangsal/1?include_rooms=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "nama_bangsal": "Bangsal Mawar",
  "kode_bangsal": "MW-001",
  "kapasitas_total": 20,
  "jumlah_kamar": 5,
  "tempat_tidur_tersedia": 15,
  "tempat_tidur_terisi": 5,
  "occupancy_rate": 25.0,
  "available_beds": 15,
  "departemen": "Internal Medicine",
  "jenis_bangsal": "Kelas I",
  "kategori": "Rawat Inap",
  "lantai": 2,
  "gedung": "Gedung Utama",
  "is_active": true,
  "is_emergency_ready": false,
  "kepala_bangsal": "Dr. Sarah Wijaya",
  "perawat_jaga": "Ns. Rina Sari",
  "tarif_per_hari": 500000.0,
  "created_at": "2025-09-19T01:00:00",
  "updated_at": "2025-09-19T01:00:00"
}
```

### 4. Get Bangsal by Code
Mendapatkan bangsal berdasarkan kode unik.

**Endpoint:** `GET /bangsal/kode/{kode_bangsal}`

```bash
curl -X GET "http://localhost:8000/api/v1/bangsal/kode/MW-001" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5. Update Bangsal
Mengupdate informasi bangsal.

**Endpoint:** `PUT /bangsal/{bangsal_id}`  
**Role Required:** Admin, Doctor, Nurse

```bash
curl -X PUT "http://localhost:8000/api/v1/bangsal/1" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "kepala_bangsal": "Dr. Sarah Wijaya Baru",
    "tarif_per_hari": 550000.0,
    "keterangan": "Updated bangsal information"
  }'
```

### 6. Delete Bangsal
Menghapus bangsal (soft delete).

**Endpoint:** `DELETE /bangsal/{bangsal_id}`  
**Role Required:** Admin

```bash
# Soft delete (set inactive)
curl -X DELETE "http://localhost:8000/api/v1/bangsal/1" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Hard delete (permanent)
curl -X DELETE "http://localhost:8000/api/v1/bangsal/1?hard_delete=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 7. Update Bed Capacity
Mengupdate okupansi tempat tidur.

**Endpoint:** `PUT /bangsal/{bangsal_id}/capacity`  
**Role Required:** Admin, Doctor, Nurse

```bash
curl -X PUT "http://localhost:8000/api/v1/bangsal/1/capacity" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tempat_tidur_terisi": 12
  }'
```

**Response:**
```json
{
  "id": 1,
  "nama_bangsal": "Bangsal Mawar",
  "tempat_tidur_terisi": 12,
  "tempat_tidur_tersedia": 8,
  "occupancy_rate": 60.0,
  "available_beds": 8
}
```

### 8. Bulk Update Capacity
Mengupdate kapasitas multiple bangsal sekaligus.

**Endpoint:** `POST /bangsal/bulk-capacity`  
**Role Required:** Admin, Doctor, Nurse

```bash
curl -X POST "http://localhost:8000/api/v1/bangsal/bulk-capacity" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '[
    {"bangsal_id": 1, "tempat_tidur_terisi": 10},
    {"bangsal_id": 2, "tempat_tidur_terisi": 15},
    {"bangsal_id": 3, "tempat_tidur_terisi": 8}
  ]'
```

### 9. Get Emergency Ready Bangsal
Mendapatkan bangsal yang siap untuk emergency.

**Endpoint:** `GET /bangsal/emergency/ready`

```bash
curl -X GET "http://localhost:8000/api/v1/bangsal/emergency/ready" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
[
  {
    "id": 2,
    "nama_bangsal": "Bangsal Melati",
    "kode_bangsal": "ML-001",
    "tempat_tidur_tersedia": 22,
    "occupancy_rate": 26.7,
    "jenis_bangsal": "Kelas II",
    "is_emergency_ready": true
  },
  {
    "id": 3,
    "nama_bangsal": "ICU Utama",
    "kode_bangsal": "ICU-01",
    "tempat_tidur_tersedia": 3,
    "occupancy_rate": 75.0,
    "jenis_bangsal": "ICU",
    "is_emergency_ready": true
  }
]
```

### 10. Get Available Bangsal
Mendapatkan bangsal dengan tempat tidur tersedia.

**Endpoint:** `GET /bangsal/available/beds`

```bash
curl -X GET "http://localhost:8000/api/v1/bangsal/available/beds?min_beds=5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 11. Get Department Bangsal
Mendapatkan bangsal berdasarkan departemen.

**Endpoint:** `GET /bangsal/department/{departemen}`

```bash
curl -X GET "http://localhost:8000/api/v1/bangsal/department/Internal%20Medicine" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 12. Get Occupancy Statistics
Mendapatkan statistik okupansi keseluruhan.

**Endpoint:** `GET /bangsal/statistics/occupancy`

```bash
curl -X GET "http://localhost:8000/api/v1/bangsal/statistics/occupancy" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "total_bangsal": 6,
  "active_bangsal": 6,
  "total_capacity": 105,
  "total_occupied": 36,
  "total_available": 69,
  "overall_occupancy_rate": 34.3,
  "emergency_ready_bangsal": 4
}
```

### 13. Get Department Statistics
Mendapatkan statistik per departemen.

**Endpoint:** `GET /bangsal/statistics/department`

```bash
curl -X GET "http://localhost:8000/api/v1/bangsal/statistics/department" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
[
  {
    "departemen": "Internal Medicine",
    "total_bangsal": 2,
    "total_capacity": 30,
    "total_occupied": 8,
    "total_available": 22,
    "occupancy_rate": 26.7
  },
  {
    "departemen": "Critical Care",
    "total_bangsal": 1,
    "total_capacity": 12,
    "total_occupied": 9,
    "total_available": 3,
    "occupancy_rate": 75.0
  }
]
```

### 14. Get Bangsal Rooms
Mendapatkan daftar kamar dalam bangsal.

**Endpoint:** `GET /bangsal/{bangsal_id}/rooms`

```bash
# All rooms
curl -X GET "http://localhost:8000/api/v1/bangsal/1/rooms" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Available rooms only
curl -X GET "http://localhost:8000/api/v1/bangsal/1/rooms?available_only=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
[
  {
    "id": 1,
    "nomor_kamar": "MW-201",
    "nama_kamar": "Kamar Mawar 1",
    "kapasitas_kamar": 4,
    "tempat_tidur_terisi": 1,
    "jenis_kamar": "Standard",
    "is_active": true,
    "is_maintenance": false,
    "status_kebersihan": "Bersih",
    "is_available": true,
    "available_beds": 3,
    "bangsal_id": 1
  }
]
```

### 15. Create Room
Membuat kamar baru dalam bangsal.

**Endpoint:** `POST /bangsal/{bangsal_id}/rooms`  
**Role Required:** Admin, Doctor

```bash
curl -X POST "http://localhost:8000/api/v1/bangsal/1/rooms" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nomor_kamar": "MW-206",
    "nama_kamar": "Kamar Mawar 6",
    "kapasitas_kamar": 4,
    "jenis_kamar": "Standard",
    "fasilitas_kamar": "{\"AC\": true, \"TV\": false}",
    "is_active": true,
    "status_kebersihan": "Bersih"
  }'
```

### 16. Get Bangsal Types
Mendapatkan daftar jenis bangsal yang tersedia.

**Endpoint:** `GET /bangsal/types/jenis`

```bash
curl -X GET "http://localhost:8000/api/v1/bangsal/types/jenis" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
["VIP", "Kelas I", "Kelas II", "Kelas III", "ICU", "NICU", "PICU", "HCU", "Isolasi"]
```

### 17. Get Departments
Mendapatkan daftar departemen yang memiliki bangsal.

**Endpoint:** `GET /bangsal/types/departments`

```bash
curl -X GET "http://localhost:8000/api/v1/bangsal/types/departments" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 18. Validate Bangsal
Memvalidasi konsistensi data bangsal.

**Endpoint:** `POST /bangsal/{bangsal_id}/validate`  
**Role Required:** Admin, Doctor

```bash
curl -X POST "http://localhost:8000/api/v1/bangsal/1/validate" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "bangsal_id": 1,
  "bangsal_capacity": 20,
  "room_total_capacity": 20,
  "bangsal_occupied": 5,
  "room_total_occupied": 5,
  "capacity_consistent": true,
  "occupancy_consistent": true,
  "is_valid": true,
  "issues": []
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Kode bangsal 'MW-001' sudah ada"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Access denied. Required role: admin, doctor"
}
```

### 404 Not Found
```json
{
  "detail": "Bangsal not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "kapasitas_total"],
      "msg": "ensure this value is greater than or equal to 0",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

## Query Parameters

### Pagination
- `page`: Nomor halaman (default: 1)
- `per_page`: Item per halaman (default: 20, max: 100)

### Filters
- `jenis_bangsal`: Filter berdasarkan jenis bangsal
- `departemen`: Filter berdasarkan departemen
- `is_active`: Filter bangsal aktif/nonaktif
- `is_emergency_ready`: Filter bangsal siap emergency
- `min_available_beds`: Minimum tempat tidur tersedia
- `search`: Pencarian di nama, kode, atau departemen

### Additional Options
- `include_inactive`: Sertakan bangsal nonaktif
- `include_rooms`: Sertakan detail kamar
- `available_only`: Hanya kamar yang tersedia
- `hard_delete`: Penghapusan permanen

## Role-Based Access Control

| Endpoint | Viewer | Nurse | Doctor | Admin |
|----------|--------|-------|--------|-------|
| GET endpoints | ✅ | ✅ | ✅ | ✅ |
| POST create bangsal | ❌ | ❌ | ✅ | ✅ |
| PUT update bangsal | ❌ | ✅ | ✅ | ✅ |
| DELETE bangsal | ❌ | ❌ | ❌ | ✅ |
| Capacity updates | ❌ | ✅ | ✅ | ✅ |
| Validation | ❌ | ❌ | ✅ | ✅ |

## Integration Examples

### Dashboard Widget - Current Occupancy
```bash
curl -X GET "http://localhost:8000/api/v1/bangsal/statistics/occupancy" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Emergency Response - Available Emergency Beds
```bash
curl -X GET "http://localhost:8000/api/v1/bangsal/emergency/ready" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Daily Census Update - Bulk Capacity Update
```bash
curl -X POST "http://localhost:8000/api/v1/bangsal/bulk-capacity" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '[
    {"bangsal_id": 1, "tempat_tidur_terisi": 18},
    {"bangsal_id": 2, "tempat_tidur_terisi": 25},
    {"bangsal_id": 3, "tempat_tidur_terisi": 11}
  ]'
```

---

**Note:** Semua timestamp dalam format ISO 8601 UTC. Ganti `YOUR_TOKEN` dengan JWT token yang valid dari endpoint login.