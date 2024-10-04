from django.urls import path

from cvbuilder.skill import views

urlpatterns = [
    # ... other URL patterns ...

    path('cvbuilder/<int:pk>', views.SkillByCvId.as_view(), name='skill_cv_id'),  # by user id
    path('<int:pk>', views.SkillById.as_view(), name='skill'),  # by course ID

]
