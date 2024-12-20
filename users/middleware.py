
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from.models import User

user = User

class RoleMiddleware:
    """Middleware to handle role-based access control"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Define admin-only paths
            admin_paths = [
                '/admin/dashboard/',
                '/admin/shops/',
                '/admin/stores/',
                '/admin/users/',
                '/admin/analytics/'
            ]
            
            # Check if user is trying to access admin paths
            if any(request.path.startswith(path) for path in admin_paths):
                if request.user.role != 'admin':
                    messages.error(request, 'Access denied. Admin privileges required.')
                    return redirect('reptrack_trace:home')

        response = self.get_response(request)
        return response

class OfflineCheckMiddleware:
    """Middleware to handle offline functionality"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            if not self.is_api_request(request):
                return redirect('reptrack_trace:offline')
            return self.get_response(request)

    def is_api_request(self, request):
        return request.path.startswith('/api/')