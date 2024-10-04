from django.urls import path, include

from cvbuilder.certificate import views

urlpatterns = [
    # ... other URL patterns ...

    path('cv/<int:pk>', views.CertificateByCvId.as_view(), name='certificate_by_cv_id'),  # by cv id
    path('<int:pk>', views.CertificateById.as_view(), name='certificate_by_id')  # by Certificate ID

]