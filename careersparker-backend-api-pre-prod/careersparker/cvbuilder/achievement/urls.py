from django.urls import path, include

from cvbuilder.achievement import views

urlpatterns = [
    # ... other URL patterns ...

    path('cv/<int:pk>', views.AchievementByCvId.as_view(), name='achievement_by_cv_id'),  # by cv id
    path('<int:pk>', views.AchievementById.as_view(), name='achievement_by_id')  # by Achievement ID

]
