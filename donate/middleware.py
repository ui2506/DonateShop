from django.http import HttpResponseForbidden
from DonateShop.utils import check_ip_blacklist, get_client_ip

import asyncio

class IPBlacklistMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = get_client_ip(request)
        try:
            is_blacklisted = asyncio.run(check_ip_blacklist(ip))
        except RuntimeError:
            is_blacklisted = asyncio.get_event_loop().run_until_complete(
                check_ip_blacklist(ip)
            )

        if is_blacklisted:
            return HttpResponseForbidden("Your IP has been banned.")

        response = self.get_response(request)
        return response