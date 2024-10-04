from django.urls import path, include

from cvbuilder.award import views

urlpatterns = [
    # ... other URL patterns ...

    path('cv/<int:pk>', views.AwardByCvId.as_view(), name='award_by_cv_id'),  # by cv id
    path('<int:pk>', views.AwardById.as_view(), name='award_by_id')  # by Awards ID

]