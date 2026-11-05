"""The leadership team shown on About (docs/architecture.md §7)."""

from django.db import models
from django.utils.text import slugify

from apps.core.models import BaseModel, ImageMixin, OrderableMixin, PublishableMixin


class TeamMember(BaseModel, PublishableMixin, OrderableMixin, ImageMixin):
    image_upload_to = "team"

    name = models.CharField(max_length=120)
    title = models.CharField(
        "job title", max_length=160, help_text="e.g. Board Member, or Operations Director."
    )
    bio = models.TextField(
        blank=True, help_text="Markdown: **bold**, *italic*; a blank line starts a new paragraph."
    )
    linkedin_url = models.URLField("LinkedIn", blank=True)
    facebook_url = models.URLField("Facebook", blank=True)
    anchor = models.SlugField(
        max_length=80,
        unique=True,
        blank=True,
        help_text="The #name of this person on the About page. Filled in from the name.",
    )

    class Meta(OrderableMixin.Meta):  # pyright: ignore[reportIncompatibleVariableOverride]  # Meta of several abstract parents
        verbose_name = "team member"

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.anchor:
            self.anchor = self._unique_anchor()
        super().save(*args, **kwargs)

    def _unique_anchor(self) -> str:
        base = slugify(self.name)[:72] or "member"
        candidate, n = base, 2
        others = type(self)._default_manager.exclude(pk=self.pk)
        while others.filter(anchor=candidate).exists():
            candidate, n = f"{base}-{n}", n + 1
        return candidate
