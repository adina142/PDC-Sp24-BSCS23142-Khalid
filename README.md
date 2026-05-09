# PDC-Sp24-BSCS23142-Khalid
# Adina Khalid - BSCS23142

# StudySync - Resilient Distributed Systems Assignment

## 📋 Overview

This repository implements a **Circuit Breaker Pattern** for the StudySync ed-tech platform to handle external LLM API failures gracefully. The assignment addresses **Problem 3: Fault Tolerance** from the Parallel and Distributed Computing (PDC) course.

---

## 🎯 Problem Solved

**Fault Tolerance (Problem 3):** The original StudySync application made synchronous blocking calls to an external LLM API. When the LLM service became slow or unavailable, requests would hang for up to 60 seconds. This caused:

- Thread starvation
- Connection pool exhaustion
- Cascading failure across the entire application — even endpoints unrelated to the AI feature became unresponsive

---

##  Solution: Circuit Breaker Pattern

A three-state circuit breaker wraps every LLM API call:

| State | Behavior |
|-------|----------|
| **CLOSED** | Normal operation — requests flow through to the LLM API |
| **OPEN** | Circuit trips after 3 consecutive failures — all requests immediately return a cached fallback response without calling the failing API |
| **HALF-OPEN** | After a 15-second recovery timeout, one test request probes the API — success resets to CLOSED, failure reopens the circuit |

### Fallback Strategy

- Maintains a prompt-keyed cache of recent successful LLM responses
- Returns cached responses when available
- Falls back to a static message: *"AI features are temporarily unavailable. Please try again shortly."*

---

## 🏗️ Project Structure

```
PDC-Sp24-BSCS23142-Khalid/
├── Backend/
│   ├── main.py              # FastAPI application with /generate endpoint
│   ├── middleware.py         # X-Student-ID custom header middleware
│   ├── circuit_breaker.py   # CircuitBreaker class (3-state implementation)
│   ├── llm_service.py       # LLM service with circuit breaker wrapper & fallback
│   ├── test_failure.py      # Test script simulating LLM failures
│   └── requirements.txt     # Python dependencies
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

---

## 🚀 How to Run

### Prerequisites

- **Python 3.10 or higher**
- **pip** (Python package manager)

### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/PDC-Sp24-BSCS23142-Khalid.git
cd PDC-Sp24-BSCS23142-Khalid
```

### Step 2: Install Dependencies

```bash
cd Backend
pip install -r requirements.txt
```

### Step 3: Start the Server

```bash
uvicorn main:app --reload
```

If `uvicorn` is not in PATH:

```bash
python -m uvicorn main:app --reload
```

The server starts at `http://127.0.0.1:8000` (or `http://localhost:8000`)

### Step 4: Run the Tests

Open a second terminal (keep the server running in the first):

```bash
cd Backend
python test_failure.py
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check with circuit breaker state |
| GET | `/circuit-status` | Detailed circuit breaker status (state, failure count) |
| POST | `/generate` | Generate AI content (with optional failure simulation) |

### POST `/generate`

**Request Body:**

```json
{
  "prompt": "hello",
  "simulate_failure": false
}
```

**Normal Response:**

```json
{
  "status": "success",
  "response": "AI Response to: hello",
  "source": "llm_api"
}
```

**Fallback Response (circuit open):**

```json
{
  "status": "fallback",
  "response": "Hello! (cached response)",
  "source": "cache"
}
```

---

## 🧪 Test Script Details

`test_failure.py` runs four automated tests:

| Test | Description | What It Proves |
|------|-------------|----------------|
| Test 1 | Checks `X-Student-ID` header | Custom middleware is working |
| Test 2 | Normal LLM request | System works when LLM is healthy |
| Test 3 | 3 failing requests trip the circuit | Circuit breaker detects failures and opens |
| Test 4 | Fallback response with circuit open | Instant response instead of 60-second hang |

### Expected Output

```
==================================================
StudySync Circuit Breaker Tests
==================================================

[Test 1] X-Student-ID header: BSCS23142
  ✅ PASSED

[Test 2] Normal request: {'status': 'success', ...}
  ✅ PASSED

[Test 3] Triggering failures to open circuit...
  Circuit state: open, failures: 3
  ✅ Circuit is OPEN

[Test 4] Testing fallback (circuit should be OPEN)...
  Time: 0.004s
  ✅ Fallback returned instantly

==================================================
ALL TESTS PASSED!
==================================================
```

---

## 🎥 Demo Video

The demo video shows:

- **Before:** System hanging for 5 seconds (simulating 60-second timeout) without circuit breaker
- **After:** Circuit breaker returns fallback response in milliseconds

---

## 🔧 Custom Header

Every API response includes the custom HTTP header:

```
X-Student-ID: BSCS23142
```

This is implemented via FastAPI middleware in `middleware.py`.

---

## 📚 Key Distributed Systems Concepts

| Concept | Description |
|---------|-------------|
| **Circuit Breaker Pattern** | Prevents cascading failures from slow external dependencies |
| **Graceful Degradation** | Returns cached/fallback responses instead of errors |
| **Fault Tolerance** | System remains partially functional during partial outages |
| **CAP Theorem** | Prioritizes Availability and Latency over Consistency during LLM outages |
| **Fail-Fast** | Returns errors quickly rather than blocking resources on doomed requests |

---

## 📄 License

This project is submitted as part of the PDC course assignment.
