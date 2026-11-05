from django.urls import path

from apps.contact.controllers.contact_controller import ContactController

app_name = "contact"

urlpatterns = [
    path("contact/", ContactController.as_view(), name="contact"),
]
