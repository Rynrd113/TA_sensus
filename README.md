# Sensus TA - Medical Dashboard Application

Aplikasi dashboard medis untuk analisis data sensus rumah sakit dengan machine learning dan prediksi menggunakan SARIMA.

## Fitur Utama

- **Dashboard Analytics**: Visualisasi data sensus rumah sakit
- **Machine Learning**: Prediksi menggunakan model SARIMA
- **Export Data**: Export laporan dalam format Excel/PDF
- **Real-time Updates**: Data terkini dengan scheduler otomatis
- **Responsive UI**: Interface yang responsif dan user-friendly

## Struktur Project

```
TA_sensus/
├── backend/           # FastAPI backend server
├── frontend/          # React TypeScript frontend
├── db/               # SQLite database
├── logs/             # Application logs
└── requirements.txt  # Python dependencies
```

## Instalasi

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm atau yarn

### Quick Start

1. **Clone repository**
   ```bash
   git clone <repository-url>
   cd TA_sensus
   ```

2. **Install Python dependencies**
   ```bash
   python3 -m pip install -r requirements.txt
   ```

3. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Start development**
   ```bash
   # Terminal 1 - Backend
   cd backend
   python start.py

   # Terminal 2 - Frontend  
   cd frontend
   npm run dev
   ```

## Penggunaan

### Development Mode

**Backend:**
```bash
cd backend
python start.py
```

**Frontend:**
```bash
cd frontend
npm run dev
```

### Akses Aplikasi
- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:5174
- **API Docs**: http://localhost:8000/docs

### API Endpoints

- `GET /api/v1/dashboard/stats` - Dashboard statistics
- `GET /api/v1/indikator` - Medical indicators
- `POST /api/v1/prediksi` - Generate predictions
- `GET /api/v1/export` - Export data

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM
- **SQLite** - Database
- **Pandas** - Data manipulation
- **Scikit-learn** - Machine learning
- **APScheduler** - Task scheduling

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Recharts** - Data visualization
- **React Query** - Data fetching

## Database

Aplikasi menggunakan SQLite database yang tersimpan di `db/sensus.db`. Schema meliputi:

- `sensus` - Data sensus utama
- `bangsal` - Data bangsal/ruangan
- `users` - User management

## Logging

Logs aplikasi tersimpan di directory `logs/`:
- `app.log` - Application logs
- Format: JSON dengan timestamp, level, dan message

## Development

### Backend Development

```bash
cd backend
python start.py
```

### Frontend Development

```bash
cd frontend  
npm run dev
```

### Testing

```bash
# Backend tests
cd backend
python -m pytest tests/ -v

# Frontend tests
cd frontend
npm test
```

## Production Build

```bash
# Build frontend untuk production
cd frontend
npm run build

# Output: frontend/dist/
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Kill processes using ports
   pkill -f "uvicorn|vite"
   ```

2. **Database issues**
   ```bash
   # Check database file permissions
   ls -la db/sensus.db
   ```

3. **Dependencies issues**
   ```bash
   # Reinstall Python dependencies
   python3 -m pip install -r requirements.txt
   
   # Reinstall frontend dependencies
   cd frontend
   npm install
   ```

### Logs

Check application logs untuk debugging:
```bash
tail -f logs/app.log
```

## Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
