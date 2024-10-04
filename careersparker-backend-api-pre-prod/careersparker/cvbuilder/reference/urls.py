from django.urls import path, include

from cvbuilder.reference import views

urlpatterns = [
    # ... other URL patterns ...

    path('cv/<int:pk>', views.ReferenceByCvId.as_view(), name='reference_by_cv_id'),  # by cv id
    path('<int:pk>', views.ReferenceById.as_view(), name='reference_by_id')  # by reference ID

]
