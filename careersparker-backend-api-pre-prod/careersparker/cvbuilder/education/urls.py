from django.urls import path, include

from cvbuilder.education import views

urlpatterns = [
    # ... other URL patterns ...

    path('cv/<int:pk>', views.EducationByCvId.as_view(), name='cv_education_id'),  # by user id
    path('<int:pk>', views.EducationById.as_view(), name='education'),  # by employment history ID

]
