from django.urls import path, include
from rest_framework.routers import DefaultRouter

from cvbuilder.employment_history import views

urlpatterns = [
    # ... other URL patterns ...

    path('cv/<int:pk>', views.EmploymentHistoryByCvId.as_view(), name='employment_history'),  # by user id
    path('<int:pk>', views.EmploymentHistoryById.as_view(), name='employment_history'),  # by employment history ID

]
