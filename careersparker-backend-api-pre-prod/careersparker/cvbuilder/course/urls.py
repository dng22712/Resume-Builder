from django.urls import path, include

from cvbuilder.course import views

urlpatterns = [
    # ... other URL patterns ...

    path('cv/<int:pk>', views.CourseByCvId.as_view(), name='course_by_cv_id'),  # by cv id
    path('<int:pk>', views.CourseById.as_view(), name='course_by_id')  # by course ID

]
