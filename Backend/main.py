# backend/main.py

from fastapi import FastAPI
from pydantic import BaseModel
from middleware import StudentIDMiddleware
from llm_service import get_llm_response, llm_circuit_breaker

app = FastAPI()
app.add_middleware(StudentIDMiddleware)

class GenerateRequest(BaseModel):
    prompt: str
    simulate_failure: bool = False

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "circuit_state": llm_circuit_breaker.state.value
    }

@app.get("/circuit-status")
async def circuit_status():
    return {
        "state": llm_circuit_breaker.state.value,
        "failure_count": llm_circuit_breaker.failure_count
    }

@app.post("/generate")
async def generate(request: GenerateRequest):
    """Generate content with circuit breaker protection.
    Set simulate_failure=true to test the circuit breaker."""
    result = await get_llm_response(request.prompt, request.simulate_failure)
    return result