from django.urls import path

from cvbuilder.text import views

urlpatterns = [
    # ... other URL patterns ...

    path('cvbuilder/<int:pk>', views.TextByCvId.as_view(), name='text_cv_id'),  # by user id
    path('<int:pk>', views.TextById.as_view(), name='text'),  # by text ID

]
