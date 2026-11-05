from django.urls import path

from apps.pages.controllers.page_controller import (
    AboutController,
    HomeController,
    ServicesController,
)

app_name = "pages"

urlpatterns = [
    path("", HomeController.as_view(), name="home"),
    path("about/", AboutController.as_view(), name="about"),
    path("services/", ServicesController.as_view(), name="services"),
]
