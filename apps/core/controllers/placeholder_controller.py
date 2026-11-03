"""The home page until Day 2 builds the layout and Day 5 builds Home."""

from django.views.generic import TemplateView


class PlaceholderController(TemplateView):
    template_name = "core/placeholder.html"
