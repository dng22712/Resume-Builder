from django.urls import path, include

from cvbuilder.cv_template import views

app_name = 'cv_template'


urlpatterns = [
    # ... other URL patterns ...

    path('cv/<int:pk>', views.TemplateByCvId.as_view(), name='template_by_cv_id'),  # by cv id
    path('<int:pk>', views.TemplateById.as_view(), name='template_by_id')  # by cv template ID

]
