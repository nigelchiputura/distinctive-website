from django.urls import path

from apps.pages.controllers.page_controller import (
    AboutController,
    HomeController,
    ServicesController,
)
from apps.pages.controllers.seo_controller import RobotsController, SitemapController

app_name = "pages"

urlpatterns = [
    path("", HomeController.as_view(), name="home"),
    path("about/", AboutController.as_view(), name="about"),
    path("services/", ServicesController.as_view(), name="services"),
    path("sitemap.xml", SitemapController.as_view(), name="sitemap"),
    path("robots.txt", RobotsController.as_view(), name="robots"),
]
