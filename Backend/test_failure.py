# backend/test_failure.py

import httpx
import time
import asyncio

BASE_URL = "http://localhost:8000"

async def check_header():
    """Test 1: Verify X-Student-ID header is present"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        student_id = response.headers.get("x-student-id")
        print(f"[Test 1] X-Student-ID header: {student_id}")
        assert student_id is not None, "FAIL: X-Student-ID header MISSING!"
        print("  ✅ PASSED\n")

async def test_normal_request():
    """Test 2: Normal LLM request works"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/generate",
            json={"prompt": "hello", "simulate_failure": False}
        )
        data = response.json()
        print(f"[Test 2] Normal request: {data}")
        assert data["source"] == "llm_api"
        assert data["status"] == "success"
        print("  ✅ PASSED\n")

async def test_circuit_breaker():
    """Test 3: Circuit breaker opens after failures and returns fallback"""
    async with httpx.AsyncClient(timeout=120.0) as client:
        print("[Test 3] Triggering failures to open circuit...")
        print("  (Each request will take ~60 seconds to timeout)")
        print("  Waiting for 3 failures to trip the circuit breaker...\n")
        
        # Send 3 requests with failure to open the circuit
        for i in range(3):
            print(f"  Sending request {i+1} with simulate_failure=true...")
            try:
                response = await client.post(
                    f"{BASE_URL}/generate",
                    json={"prompt": "hello", "simulate_failure": True},
                    timeout=120.0
                )
                data = response.json()
                print(f"  Response {i+1}: status={data['status']}, source={data['source']}")
            except httpx.TimeoutException:
                print(f"  Response {i+1}: Timeout after 120s")
            except Exception as e:
                print(f"  Response {i+1}: Error - {e}")
        
        # Check circuit state
        print("\n  Checking circuit status...")
        status = await client.get(f"{BASE_URL}/circuit-status")
        circuit = status.json()
        print(f"  Circuit state: {circuit['state']}, failures: {circuit['failure_count']}")
        assert circuit["state"] == "open", f"Expected 'open', got '{circuit['state']}'"
        print("  ✅ Circuit is OPEN\n")
        
        # Now make a request without failure - should get fallback instantly
        print("[Test 4] Testing fallback (circuit should be OPEN)...")
        start = time.time()
        response = await client.post(
            f"{BASE_URL}/generate",
            json={"prompt": "hello", "simulate_failure": False}
        )
        elapsed = time.time() - start
        data = response.json()
        print(f"  Response: {data}")
        print(f"  Time: {elapsed:.3f}s")
        assert data["source"] == "cache", f"Expected 'cache', got '{data['source']}'"
        assert data["status"] == "fallback"
        assert elapsed < 1.0, f"Fallback took {elapsed:.3f}s, should be < 1s"
        print("  ✅ Fallback returned instantly\n")

async def main():
    print("=" * 50)
    print("StudySync Circuit Breaker Tests")
    print("=" * 50 + "\n")
    
    await check_header()
    await test_normal_request()
    await test_circuit_breaker()
    
    print("=" * 50)
    print("ALL TESTS PASSED!")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())