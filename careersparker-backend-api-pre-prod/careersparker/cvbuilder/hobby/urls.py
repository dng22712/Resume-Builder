from django.urls import path, include

from cvbuilder.hobby import views

urlpatterns = [
    # ... other URL patterns ...

    path('cv/<int:pk>', views.HobbyByCvId.as_view(), name='hobby_by_cv_id'),  # by cv id
    path('<int:pk>', views.HobbyById.as_view(), name='hobby_by_id')  # by hobby ID

]
