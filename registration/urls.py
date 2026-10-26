from django.urls import path

from . import views

app_name = "registration"

urlpatterns = [
    path("", views.index, name="index"),
    path("<slug:country_code>/", views.register, name="register"),
    path("<slug:country_code>/success/", views.success, name="success"),
    path("<slug:country_code>/duplicate/", views.duplicate, name="duplicate"),
]
