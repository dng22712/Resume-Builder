"""
URL mapping for the user API
"""

from django.urls import path
from rest_framework import routers

from user import views
from user.views import CreateTokenView, RefreshTokenView

app_name = 'user'

router = routers.DefaultRouter()
router.register('user', views.CreateUserView, basename='user')
router.register('user', views.ManageUserView, basename='manage_user')

urlpatterns = [
    path(
        'register/',
        views.CreateUserView.as_view(),
        name='register'
    ),
    path(
        'login/',
        CreateTokenView.as_view(),
        name='token_obtain_pair'
    ),  # Use Simple JWT for login

    path(
        'login/refresh/',
        RefreshTokenView.as_view(),
        name='token_refresh'
    ),  # Token refresh
    path(
        'forgot_password/',
        views.ForgotPassword.as_view(),
        name='forgot_password'
    ),

    path(
        'login/facebook/',
        views.FacebookLogin.as_view(),
        name='facebook-login'
    ),
    path(
        'login/linkedin/',
        views.LinkedInLogin.as_view(),
        name='linkedin-login'
    ),
    path(
        'login/google/',
        views.GoogleLogin.as_view(),
        name='google-login'
    ),
    path(
        'logout/',
        views.Logout.as_view(),
        name='logout'
    ),
    # path(
    #     'deactivate_account/',
    #     views.deactivate_account.as_view(),
    #     name='activate_account'
    # ),
    path(
        'change_password/',
        views.ChangePasswordView.as_view(),
        name='change_password'
    ),

    path(
        'verify-account/<str:uidb64>/<str:token>/',
        views.ActivateAccount.as_view(), name='verify-account'),
    path(
        'forgot_password_confirm/<str:uidb64>/<str:token>/',
        views.ForgotPasswordConfirm.as_view(),
        name='forgot_password_confirm'
    ),
    #
    # path(
    #     'block/',
    #     BlockUser.as_view(),
    #     name='block_user'
    # ),
    path(
        'delete_account/<int:pk>/',
        views.DeleteAccount.as_view(),
        name='delete_account'
    ),
    # path(
    #     'swagger-login/',
    #     SwaggerLoginView.as_view(),
    #     name='swagger-login'
    # ),

]

