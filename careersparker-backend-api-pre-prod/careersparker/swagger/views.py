from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy

from util.Permission.swagger_permission import SwaggerPermission


class SwaggerLoginView(LoginView):
    """

    """

    permission_classes = [SwaggerPermission]
    template_name = 'rest_framework_swagger/swagger_login.html'  # Create a login template
    success_url = reverse_lazy('api')  # Redirect to the API documentation after successful login

    def form_valid(self, form):
        """

        """


        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(self.request, username=username, password=password)

        # convert self.request.user to a readable string
        if user:

            if SwaggerPermission.has_swagger_permission(user):
                login(self.request, user)  # add jwt token to the user
                return redirect(self.success_url)

            else:
                form.add_error(None, 'Invalid username or password')
                return render(self.request, self.template_name, {'form': form})
        else:
            return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)
