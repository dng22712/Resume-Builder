from django.urls import path, include

from cvbuilder.language import views

urlpatterns = [
    # ... other URL patterns ...

    path('cv/<int:pk>', views.LanguageByCvId.as_view(), name='Language_by_cv_id'),  # by cv id
    path('<int:pk>', views.LanguageById.as_view(), name='Language_by_id')  # by volunteering ID

]
