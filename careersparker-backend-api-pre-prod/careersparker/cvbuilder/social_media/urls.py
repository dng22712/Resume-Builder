from django.urls import path, include

from cvbuilder.social_media import views

urlpatterns = [
    # ... other URL patterns ...

    path('cv/<int:pk>', views.SocialMediaByCvId.as_view(), name='social_media_by_cv_id'),  # by cv id
    path('<int:pk>', views.SocialMediaById.as_view(), name='social_media_by_id')  # by social_media ID

]
