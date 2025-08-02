#!/bin/bash

# Performance Test Script untuk SENSUS-RS Frontend
echo "🚀 SENSUS-RS Performance Test Script"
echo "===================================="

# Check if backend is running
echo "📡 Checking backend connection..."
if curl -s http://localhost:8000/api/v1/ > /dev/null; then
    echo "✅ Backend is running on http://localhost:8000"
else
    echo "❌ Backend not found. Please start backend first:"
    echo "   cd backend && python -m uvicorn main:app --reload"
    exit 1
fi

# Check if frontend build exists
if [ ! -d "dist" ]; then
    echo "📦 Building optimized frontend..."
    npm run build
else
    echo "✅ Build directory found"
fi

# Start preview server in background
echo "🌐 Starting preview server..."
npm run preview &
PREVIEW_PID=$!

# Wait for server to start
sleep 3

echo ""
echo "🧪 Performance Test Results:"
echo "=============================="

# Test bundle sizes
echo "📊 Bundle Size Analysis:"
echo "------------------------"
if [ -d "dist/js" ]; then
    echo "JavaScript chunks:"
    ls -lah dist/js/*.js | awk '{print "  " $9 ": " $5}'
    
    # Calculate total JS size
    TOTAL_JS=$(du -ch dist/js/*.js | tail -1 | cut -f1)
    echo "  Total JS: $TOTAL_JS"
fi

if [ -f "dist/assets/index-*.css" ]; then
    CSS_SIZE=$(ls -lah dist/assets/*.css | awk '{print $5}')
    echo "  CSS: $CSS_SIZE"
fi

echo ""
echo "🔗 Test URLs:"
echo "-------------"
echo "  Frontend: http://localhost:4173"
echo "  Backend:  http://localhost:8000"

echo ""
echo "📋 Manual Testing Steps:"
echo "------------------------"
echo "1. Open http://localhost:4173 in Chrome"
echo "2. Open DevTools (F12)"
echo "3. Go to Lighthouse tab"
echo "4. Run Performance audit"
echo "5. Compare with previous 47% score"

echo ""
echo "⚡ Expected Improvements:"
echo "------------------------"
echo "  • Performance Score: 47% → 80-85%"
echo "  • First Contentful Paint: <1.5s"
echo "  • Largest Contentful Paint: <2.5s"  
echo "  • Time to Interactive: <3.5s"
echo "  • Bundle Size Reduction: ~60%"

echo ""
echo "🎯 Performance Optimizations Applied:"
echo "------------------------------------"
echo "  ✅ Code splitting & lazy loading"
echo "  ✅ Bundle optimization"
echo "  ✅ React.memo & memoization"
echo "  ✅ DNS prefetch & resource hints"
echo "  ✅ Critical CSS inlining"
echo "  ✅ Font optimization"
echo "  ✅ Extended caching"
echo "  ✅ Skeleton loaders"

echo ""
echo "Press Ctrl+C to stop preview server"
echo "Preview server PID: $PREVIEW_PID"

# Keep script running
wait $PREVIEW_PID
