#!/bin/bash

echo "🏥 SENSUS-RS Quick E2E Integration Testing (No Training)"
echo "======================================================="

BACKEND_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:5174"
PASSED_TESTS=0
TOTAL_TESTS=8

echo "Starting Quick End-to-End Integration Tests..."
echo ""

# Test 1: Backend Health
echo "[1/8] Testing Backend Health..."
RESPONSE=$(curl -s -w "%{http_code}" -o /dev/null "$BACKEND_URL/health")
if [ "$RESPONSE" = "200" ]; then
    echo "✅ Backend server is running"
    ((PASSED_TESTS++))
else
    echo "❌ Backend server not responding (HTTP: $RESPONSE)"
fi
echo ""

# Test 2: Dashboard API
echo "[2/8] Testing Dashboard API..."
RESPONSE=$(curl -s "$BACKEND_URL/api/v1/dashboard/overview")
if [[ $RESPONSE == *"bor"* ]]; then
    BOR_VALUE=$(echo $RESPONSE | grep -o '"bor":[0-9.]*' | cut -d':' -f2)
    echo "✅ Dashboard API working"
    echo "Sample data: ${BOR_VALUE}% BOR"
    ((PASSED_TESTS++))
else
    echo "❌ Dashboard API failed"
    echo "Response: $RESPONSE"
fi
echo ""

# Test 3: SARIMA Status API (Public)
echo "[3/8] Testing SARIMA Status API..."
RESPONSE=$(curl -s "$BACKEND_URL/api/v1/sarima/status")
if [[ $RESPONSE == *"model_trained"* ]]; then
    MODEL_STATUS=$(echo $RESPONSE | grep -o '"model_trained":[a-z]*' | cut -d':' -f2)
    echo "✅ SARIMA Status API working"
    echo "Model trained: $MODEL_STATUS"
    ((PASSED_TESTS++))
else
    echo "❌ SARIMA Status API failed"
    echo "Response: $RESPONSE..."
fi
echo ""

# Test 4: Database Connection
echo "[4/8] Testing Database Connection..."
RESPONSE=$(curl -s "$BACKEND_URL/api/v1/sensus?limit=5")
if [[ $RESPONSE == *"data"* ]]; then
    COUNT=$(echo $RESPONSE | grep -o '"data":\[.*\]' | tr ',' '\n' | grep -c '"id"')
    echo "✅ Database connection working"
    echo "Sample records: $COUNT"
    ((PASSED_TESTS++))
else
    echo "❌ Database connection failed"
fi
echo ""

# Test 5: Frontend Health (Quick Check)
echo "[5/8] Testing Frontend Health..."
RESPONSE=$(curl -s -w "%{http_code}" -o /dev/null --max-time 10 "$FRONTEND_URL")
if [ "$RESPONSE" = "200" ]; then
    echo "✅ Frontend server is running"
    ((PASSED_TESTS++))
else
    echo "❌ Frontend server not responding (HTTP: $RESPONSE)"
fi
echo ""

# Test 6: CORS Configuration
echo "[6/8] Testing CORS Configuration..."
CORS_RESPONSE=$(curl -s -H "Origin: http://localhost:5174" -H "Access-Control-Request-Method: GET" -H "Access-Control-Request-Headers: X-Requested-With" -X OPTIONS "$BACKEND_URL/api/v1/dashboard/overview")
if [ $? -eq 0 ]; then
    echo "✅ CORS configuration tested"
    ((PASSED_TESTS++))
else
    echo "❌ CORS configuration issue"
fi
echo ""

# Test 7: API Performance (Quick)
echo "[7/8] Testing API Performance..."
START_TIME=$(date +%s%N)
curl -s "$BACKEND_URL/api/v1/dashboard/overview" > /dev/null
END_TIME=$(date +%s%N)
DURATION=$(( ($END_TIME - $START_TIME) / 1000000 ))

if [ $DURATION -lt 1000 ]; then
    echo "✅ API performance good (${DURATION}ms)"
    ((PASSED_TESTS++))
else
    echo "⚠️ API response slow (${DURATION}ms)"
fi
echo ""

# Test 8: Error Handling
echo "[8/8] Testing Error Handling..."
RESPONSE=$(curl -s -w "%{http_code}" -o /dev/null "$BACKEND_URL/api/v1/nonexistent")
if [ "$RESPONSE" = "404" ]; then
    echo "✅ 404 error handling working"
    ((PASSED_TESTS++))
else
    echo "❌ Error handling issue (Expected 404, got $RESPONSE)"
fi
echo ""

# Summary
echo "======================================================"
echo "Quick Integration Test Summary:"
echo "Tests passed: $PASSED_TESTS/$TOTAL_TESTS"

if [ $PASSED_TESTS -eq $TOTAL_TESTS ]; then
    echo "🎉 All tests passed - system ready!"
    exit 0
elif [ $PASSED_TESTS -ge 6 ]; then
    echo "⚠️ Most tests passed - system functional"
    echo "Minor issues may need attention"
    exit 1
else
    echo "❌ Multiple failures detected - system needs attention"
    echo "Please check server status and configuration"
    exit 1
fi

echo ""
echo "Next steps:"
echo "1. Run full UI/UX testing in browser"
echo "2. Test SARIMA training manually if needed"
echo "3. Continue with performance optimization"
echo "4. Clean up file structure"