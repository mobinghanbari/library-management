import logging
from datetime import datetime
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger("api_logger")
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler(f"logs/logs_{datetime.now().strftime('%Y-%m-%d')}.txt")
        handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.logger.addHandler(handler)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        path = request.url.path
        method = request.method
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"IP: {client_ip} - Path: {path} - Method: {method} - Time: {timestamp}"
        self.logger.info(log_message)
        response = await call_next(request)
        return response
