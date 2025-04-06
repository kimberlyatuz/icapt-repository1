# Updated middleware.py
from django.shortcuts import redirect
from django.conf import settings

class GroupAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Paths that don't require authentication
        public_paths = [
            '/', '/login/', '/logout/', 
            '/register/', '/unauthorized/'
        ]
        
        if request.path in public_paths:
            return None
            
        if request.user.is_authenticated:
            if not request.user.groups.exists():
                return redirect('unauthorized')
        else:
            return redirect('landing')
        return None
