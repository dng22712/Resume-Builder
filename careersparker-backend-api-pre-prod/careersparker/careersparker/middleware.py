from django.shortcuts import redirect
from rest_framework.reverse import reverse


class RedirectUnauthenticatedSwaggerToLoginMiddleware:  # middleware for swagger login
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated and request.path.startswith('/api/'):
            return redirect(reverse('swagger-login'))

        response = self.get_response(request)
        return response
