import logging
import httpagentparser

logger = logging.getLogger("access")

class RealIPLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        real_ip = request.META.get("HTTP_X_REAL_IP") or request.META.get("REMOTE_ADDR")
        user_agent = request.META.get("HTTP_USER_AGENT", "-")

        os_name, browser = httpagentparser.simple_detect(user_agent) or ("UnknownOS", "UnknownBrowser")

        response = self.get_response(request)

        record = {
            "ip": real_ip,
            "os": os_name,
            "browser": browser,
            "method": request.method,
            "path": request.get_full_path(),
            "status": response.status_code,
        }

        logger.info("", extra=record)
        return response