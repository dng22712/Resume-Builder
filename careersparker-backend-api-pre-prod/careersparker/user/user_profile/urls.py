

from django.urls import path, include
from rest_framework import routers
from rest_framework.routers import DefaultRouter

from user.user_profile import views
from user.user_profile.views import UserProfileByUserName, ProfilePictureView
from user.views import CreateTokenView, RefreshTokenView

app_name = 'user_profile'

router = DefaultRouter()


urlpatterns = [
    path('', include(router.urls)),
    path('<int:pk>', views.UserProfileUpdate.as_view(), name='profile-update'),
    path('<str:username>', UserProfileByUserName.as_view(), name='profile-by-username'),

    # #profile Images
    path('profile_pictures/<int:pk>', views.ProfilePictureView.as_view(), name='profile_picture'),

    ]
