from django.urls import path



urlpatterns = [
    # ... other URL patterns ...

    path('cvbuilder/<int:pk>', views.GraphByCvId.as_view(), name='strength_cv_id'),  # by user id
    path('<int:pk>', views.GraphById.as_view(), name='strength'),  # by strength ID

]
