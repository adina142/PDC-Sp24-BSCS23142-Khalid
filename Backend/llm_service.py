# backend/llm_service.py

import asyncio
from circuit_breaker import CircuitBreaker, CircuitBreakerOpenError

# Create one circuit breaker instance
llm_circuit_breaker = CircuitBreaker(
    failure_threshold=3,
    recovery_timeout=15  # 15 seconds for demo
)

# Simple fallback cache
fallback_cache = {
    "hello": "Hello! (cached response)",
    "default": "AI features are temporarily unavailable. Please try again shortly.",
}

async def call_llm_api(prompt: str, simulate_failure: bool = False):
    """Simulated LLM API call"""
    if simulate_failure:
        await asyncio.sleep(5)  # Simulate the 60-second timeout
        raise Exception("LLM API timeout after 5 seconds")
    
    # Normal fast response
    await asyncio.sleep(0.1)
    return f"AI Response to: {prompt}"

async def get_llm_response(prompt: str, simulate_failure: bool = False):
    """Get LLM response with circuit breaker and fallback"""
    try:
        response = await llm_circuit_breaker.call(call_llm_api, prompt, simulate_failure)
        return {
            "status": "success",
            "response": response,
            "source": "llm_api"
        }
    except CircuitBreakerOpenError:
        # Circuit is open - return fallback immediately
        fallback = fallback_cache.get(prompt.lower(), fallback_cache["default"])
        return {
            "status": "fallback",
            "response": fallback,
            "source": "cache"
        }
    except Exception as e:
        # Other failures - also return fallback
        fallback = fallback_cache.get(prompt.lower(), fallback_cache["default"])
        return {
            "status": "fallback",
            "response": fallback,
            "source": "cache",
            "error": str(e)
        }