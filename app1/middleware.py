
from django.shortcuts import redirect
from django.conf import settings

class GroupAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Skip middleware for these paths
        if request.path in ['/login/', '/logout/', '/register/', '/']:
            return None
            
        if request.user.is_authenticated:
            if not request.user.groups.exists():
                return redirect('unauthorized')
        return None
