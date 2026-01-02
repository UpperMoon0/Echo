import sys
import os
sys.path.insert(0, '/app/Echo')

from fastapi import FastAPI
import uvicorn
from api.routes import router

# Initialize FastAPI app
app = FastAPI(
    title="Echo",
    description="Speech-to-text service with Whisper and MCP support",
    version="1.0.0"
)

# Add Request Logging Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("echo-request-logger")

class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f"Incoming Request: {request.method} {request.url}")
        logger.info(f"Headers: {request.headers}")
        response = await call_next(request)
        logger.info(f"Response Status: {response.status_code}")
        return response

app.add_middleware(RequestLoggerMiddleware)

app.include_router(router)

def main():
    """Start the unified server (REST API + Embedded MCP)."""
    port = int(os.getenv("PORT", "8000"))
    print(f"Starting Echo server on port {port} (HTTP + Embedded MCP)")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port
    )

if __name__ == "__main__":
    main()