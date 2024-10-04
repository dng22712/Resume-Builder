from django.urls import path, include

from cvbuilder.publication import views

urlpatterns = [
    # ... other URL patterns ...

    path('cv/<int:pk>', views.PublicationByCvId.as_view(), name='publication_by_cv_id'),  # by cv id
    path('<int:pk>', views.PublicationById.as_view(), name='publication_by_id')  # by publication ID

]
