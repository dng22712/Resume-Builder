from django.urls import path, include
from rest_framework.routers import DefaultRouter

from cvbuilder import views

app_name = 'cvbuilder'
router = DefaultRouter()
router.register('', views.CvBuilderViewset, basename='cvbuilder')


urlpatterns = [
    # ... other URL patterns ...
    path('', include(router.urls)),

    # path('create/', StripeCvBuilderPayment.as_view(), name='create'),
    path('update-cv/<int:pk>', views.CvBuilderUpdate.as_view(), name='cv-update'),
    path('cv-word-download', views.CvWordDownload.as_view(), name='cv-word-download'),
    path('cv-pdf-download', views.CvPdfDownload.as_view(), name='cv-pdf-download'),

]
