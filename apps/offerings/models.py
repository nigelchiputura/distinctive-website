"""The consulting services Distinctive offers (docs/architecture.md §7).

Each has a stable `anchor`, the #name of its band on the Services page; Home's cards link to
/services/#<anchor>.
"""

from django.db import models
from django.utils.text import slugify

from apps.core.models import BaseModel, ImageMixin, OrderableMixin, PublishableMixin


class Service(BaseModel, PublishableMixin, OrderableMixin, ImageMixin):
    image_upload_to = "services"

    title = models.CharField(max_length=120)
    anchor = models.SlugField(
        max_length=80,
        unique=True,
        blank=True,
        help_text="The #name of this service on the Services page. Filled in from the title if "
        "left empty, then kept, so links keep working if the title changes.",
    )
    summary = models.CharField(
        max_length=200, blank=True, help_text="One or two lines, shown on the Home page card."
    )
    body = models.TextField(
        blank=True,
        help_text="The full description on the Services page. Markdown: **bold**, *italic*, lists.",
    )
    show_on_home = models.BooleanField(
        "show on Home",
        default=False,
        help_text="Home shows up to six services, in this order.",
    )

    class Meta(OrderableMixin.Meta):  # pyright: ignore[reportIncompatibleVariableOverride]  # Meta of several abstract parents
        verbose_name = "service"

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.anchor:
            self.anchor = self._unique_anchor()
        super().save(*args, **kwargs)

    def _unique_anchor(self) -> str:
        base = slugify(self.title)[:72] or "service"
        candidate, n = base, 2
        others = type(self)._default_manager.exclude(pk=self.pk)
        while others.filter(anchor=candidate).exists():
            candidate, n = f"{base}-{n}", n + 1
        return candidate
