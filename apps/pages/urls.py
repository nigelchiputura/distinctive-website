from django.urls import path

from apps.pages.controllers.home_controller import HomeController

app_name = "pages"

urlpatterns = [
    path("", HomeController.as_view(), name="home"),
]
