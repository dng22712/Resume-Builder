from django.urls import path

from cvbuilder.graph import views

urlpatterns = [
    # ... other URL patterns ...

    path('cvbuilder/<int:pk>', views.GraphByCvId.as_view(), name='strength_cv_id'),  # by cv id
    path('<int:pk>', views.GraphById.as_view(), name='strength'),  # by Graph ID

]
