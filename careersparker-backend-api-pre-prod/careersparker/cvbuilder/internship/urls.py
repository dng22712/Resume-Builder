from django.urls import path, include

from cvbuilder.internship import views

urlpatterns = [
    # ... other URL patterns ...

    path('cv/<int:pk>', views.InternshipByCvId.as_view(), name='internship_by_cv_id'),  # by cv id
    path('<int:pk>', views.InternshipById.as_view(), name='internship_by_id')  # by internship ID

]
