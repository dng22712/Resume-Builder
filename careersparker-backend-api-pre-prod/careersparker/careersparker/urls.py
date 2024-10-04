"""
URL configuration for careersparker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from drf_spectacular.openapi import AutoSchema
from rest_framework_simplejwt.authentication import JWTAuthentication


from swagger.views import SwaggerLoginView
from user import user_profile


class CustomSpectacularSwaggerView(SpectacularSwaggerView):
    authentication_classes = [JWTAuthentication]


urlpatterns = [
    # Admin urls
    path('admin/', admin.site.urls),

    # API urls
    path('swagger-login/', SwaggerLoginView.as_view(), name='swagger-login'),
    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path('api/', CustomSpectacularSwaggerView.as_view(url_name='api-schema'), name='api-docs'),
    path('api/', SpectacularSwaggerView.as_view(url_name='api-schema'), name='api'),

    # User urls
    path('user/', include('user.urls'), name='user'),
    path('user_profile/', include('user.user_profile.urls'), name='user_profile'),

    # Payment urls
    path('payment/', include('fixed_payments.urls'), name='payment'),
    path('subscription/', include('subscription_payments.urls'), name='subscription'),

    # CV Builder urls
    path('cvbuilder/', include('cvbuilder.urls'), name='cvbuilder'),
    path('cvbuilder/employment-history/', include('cvbuilder.employment_history.urls'), name='employment-history'),
    path('cvbuilder/education/', include('cvbuilder.education.urls'), name='education'),
    path('cvbuilder/skill/', include('cvbuilder.skill.urls'), name='skill'),
    path('cvbuilder/award/', include('cvbuilder.award.urls'), name='award'),
    path('cvbuilder/certificate/', include('cvbuilder.certificate.urls'), name='certification'),
    path('cvbuilder/publication/', include('cvbuilder.publication.urls'), name='publication'),
    path('cvbuilder/hobby/', include('cvbuilder.hobby.urls'), name='hobby'),
    path('cvbuilder/achievement/', include('cvbuilder.achievement.urls'), name='achievement'),
    path('cvbuilder/reference/', include('cvbuilder.reference.urls'), name='reference'),
    path('cvbuilder/course/', include('cvbuilder.course.urls'), name='course'),
    path('cvbuilder/language/', include('cvbuilder.language.urls'), name='language'),
    path('cvbuilder/volunteering/', include('cvbuilder.volunteering.urls'), name='volunteering'),
    path('cvbuilder/internship/', include('cvbuilder.internship.urls'), name='internship'),
    path('cvbuilder/social_media/', include('cvbuilder.social_media.urls'), name='social-media'),
    path('cvbuilder/strength/', include('cvbuilder.strength.urls'), name='strength'),
    path('cvbuilder/custom_section/', include('cvbuilder.custom_section.urls'), name='custom-section'),
    path('cvbuilder/template/', include('cvbuilder.cv_template.urls'), name='template'),
    path('cvbuilder/template_list/', include('cvbuilder.cv_template_list.urls'), name='template-list'),
]
