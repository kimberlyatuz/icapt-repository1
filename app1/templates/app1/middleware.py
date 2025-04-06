from django.shortcuts import redirect
from django.conf import settings

class GroupAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated:
            if not any(request.user.groups.filter(name__in=settings.AUTH_GROUPS.values())):
                return redirect('unauthorized')
        return None
