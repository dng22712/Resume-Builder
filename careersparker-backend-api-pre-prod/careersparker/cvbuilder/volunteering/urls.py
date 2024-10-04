from django.urls import path, include

from cvbuilder.volunteering import views

urlpatterns = [
    # ... other URL patterns ...

    path('cv/<int:pk>', views.VolunteeringByCvId.as_view(), name='volunteering_by_cv_id'),  # by cv id
    path('<int:pk>', views.VolunteeringById.as_view(), name='volunteering_by_id')  # by volunteering ID

]
