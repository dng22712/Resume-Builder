"""
Category List URL
"""

from rest_framework.routers import DefaultRouter
from django.urls import path

from cvbuilder.cv_template_list import views

router = DefaultRouter()

app_name = 'categoryList'

urlpatterns = [
    # Category List URL Mapping
    path('', views.CVTemplateListViewSet.as_view(), name='categoryList'),
]
