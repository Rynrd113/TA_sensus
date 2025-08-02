#!/bin/bash
# start_system.sh - Script untuk menjalankan seluruh sistem

echo "🚀 STARTING SENSUS-RS SYSTEM"
echo "============================="

# Change to project directory
cd /home/rynrd/Documents/Project/TA/sensus-rs/sensus-rs

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
echo "📦 Installing Python dependencies..."
pip install -q fastapi uvicorn sqlalchemy pydantic pandas statsmodels joblib pytest requests

# Initialize database if needed
echo "💾 Initializing database..."
if [ ! -f "sensus.db" ]; then
    PYTHONPATH=. python backend/database/init_db.py
fi

# Train ML model if needed
echo "🤖 Checking ML model..."
if [ ! -f "backend/ml/model.pkl" ]; then
    echo "Training ARIMA model..."
    PYTHONPATH=. python backend/ml/train.py
fi

# Start backend server in background
echo "🔧 Starting backend server..."
PYTHONPATH=. python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Check if backend is running
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✅ Backend running on http://localhost:8000"
    echo "📖 API Documentation: http://localhost:8000/docs"
else
    echo "❌ Backend failed to start"
    exit 1
fi

# Start frontend if node_modules exists
if [ -d "frontend/node_modules" ]; then
    echo "🎨 Starting frontend..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    echo "✅ Frontend starting on http://localhost:5173"
else
    echo "⚠️  Frontend dependencies not installed. Run:"
    echo "   cd frontend && npm install && npm run dev"
fi

echo ""
echo "🎉 SYSTEM STARTED SUCCESSFULLY!"
echo "================================"
echo "🔧 Backend API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo "🎨 Frontend: http://localhost:5173"
echo ""
echo "📊 System Status:"
python3 system_check.py

echo ""
echo "🛑 To stop the system:"
echo "   kill $BACKEND_PID"
if [ ! -z "$FRONTEND_PID" ]; then
    echo "   kill $FRONTEND_PID"
fi

# Keep script running
echo ""
echo "⌨️  Press Ctrl+C to stop all services..."
trap "echo '🛑 Stopping services...'; kill $BACKEND_PID 2>/dev/null; kill $FRONTEND_PID 2>/dev/null; exit 0" INT

# Wait for interrupt
while true; do
    sleep 1
done
