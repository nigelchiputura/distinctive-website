"""Shared base models and the site settings singleton (docs/architecture.md §4)."""

from typing import ClassVar

from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class BaseModel(models.Model):
    """Every model extends this: when it was created and last changed."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class PublishableMixin(models.Model):
    """Content an editor can hide without deleting. Repositories' published() filters on it."""

    is_published = models.BooleanField(
        "published", default=True, help_text="Untick to hide this from the website."
    )
    published_at = models.DateTimeField(null=True, blank=True, editable=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.is_published and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)


class OrderableMixin(models.Model):
    """Editor-controlled order: lower numbers first, then oldest first."""

    sort_order = models.PositiveIntegerField(
        "order", default=0, db_index=True, help_text="Lower numbers appear first."
    )

    class Meta:
        abstract = True
        ordering: ClassVar = ["sort_order", "pk"]


class SluggedMixin(models.Model):
    """A unique URL slug, generated once from `slug_source_field` and then left alone, so a
    renamed title doesn't break links that are already out there."""

    slug_source_field: ClassVar[str] = "title"
    slug_max_length: ClassVar[int] = 140

    slug = models.SlugField(
        max_length=140,
        unique=True,
        blank=True,
        help_text="Used in the web address. Filled in from the title if left empty.",
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._unique_slug()
        super().save(*args, **kwargs)

    def _unique_slug(self) -> str:
        source = str(getattr(self, self.slug_source_field, "") or "")
        base = slugify(source)[: self.slug_max_length - 4] or "item"
        candidate, n = base, 2
        others = type(self)._default_manager.exclude(pk=self.pk)
        while others.filter(slug=candidate).exists():
            candidate, n = f"{base}-{n}", n + 1
        return candidate


class SiteSettings(BaseModel):
    """The company's details shown on every page. Exactly one row (pk=1), edited in the admin.

    Any field left empty falls back to the defaults in apps/core/services/site_details.py.
    """

    SINGLETON_PK = 1

    company_name = models.CharField(max_length=120, blank=True)
    tagline = models.CharField(max_length=200, blank=True)
    phone_display = models.CharField(
        "phone (as shown)", max_length=60, blank=True, help_text="e.g. +263 (24) 2 486 642 - 3"
    )
    phone_href = models.CharField(
        "phone (to dial)",
        max_length=30,
        blank=True,
        help_text="The number a phone dials when tapped, digits only after +, e.g. +263242486642",
    )
    enquiries_email = models.EmailField(blank=True)
    recruitment_email = models.EmailField(blank=True)
    address = models.CharField(max_length=200, blank=True)
    hours = models.CharField("business hours", max_length=120, blank=True)
    footer_blurb = models.TextField(blank=True)

    facebook_url = models.URLField("Facebook", blank=True)
    linkedin_url = models.URLField("LinkedIn", blank=True)
    instagram_url = models.URLField("Instagram", blank=True)
    x_url = models.URLField("X (Twitter)", blank=True)

    meta_description = models.CharField(
        "default meta description",
        max_length=300,
        blank=True,
        help_text="Shown in search results for pages that don't have their own description.",
    )
    og_image = models.ImageField(
        "default sharing image",
        upload_to="site/",
        blank=True,
        help_text="Shown when a page is shared on social media. 1200 × 630 pixels works best.",
    )
    ga_measurement_id = models.CharField(
        "Google Analytics ID",
        max_length=20,
        blank=True,
        help_text="G-XXXXXXXXXX. Loaded only after a visitor accepts cookies.",
    )
    map_query = models.CharField(
        "map location",
        max_length=200,
        blank=True,
        help_text="What the Contact page map searches for, e.g. the street address.",
    )

    class Meta(BaseModel.Meta):
        verbose_name = "site settings"
        verbose_name_plural = "site settings"
        constraints: ClassVar = [
            models.CheckConstraint(condition=models.Q(pk=1), name="site_settings_singleton"),
        ]

    def __str__(self) -> str:
        return "Site settings"

    def save(self, *args, **kwargs):
        """Always row 1. A new instance saved over the existing row keeps its creation date."""
        self.pk = self.SINGLETON_PK
        if self.created_at is None:
            self.created_at = (
                type(self)
                ._default_manager.filter(pk=self.pk)
                .values_list("created_at", flat=True)
                .first()
            )
        super().save(*args, **kwargs)
