from django.urls import path

from cvbuilder.strength import views

urlpatterns = [
    # ... other URL patterns ...

    path('cvbuilder/<int:pk>', views.StrengthByCvId.as_view(), name='strength_cv_id'),  # by user id
    path('<int:pk>', views.StrengthById.as_view(), name='strength'),  # by strength ID

]
