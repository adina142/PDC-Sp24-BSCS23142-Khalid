from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

class StudentIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # REPLACE with your actual student ID
        response.headers["X-Student-ID"] = "BSCS23142"
        return response