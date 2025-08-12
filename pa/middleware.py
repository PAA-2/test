import json
import time
import uuid
import logging

logger = logging.getLogger(__name__)


class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = uuid.uuid4().hex
        request.request_id = request_id
        start = time.perf_counter()
        response = self.get_response(request)
        duration = (time.perf_counter() - start) * 1000
        user_id = None
        if hasattr(request, "user") and request.user.is_authenticated:
            user_id = request.user.id
        logger.info(
            json.dumps(
                {
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.get_full_path(),
                    "status": response.status_code,
                    "duration_ms": round(duration, 2),
                    "user_id": user_id,
                }
            )
        )
        return response
