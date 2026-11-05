"""Pages and the blocks they are built from (docs/architecture.md §7).

A Page is one of the site's fixed pages (Home, About, Services, Contact), created by a migration.
Its content is a list of PageSections an editor can add, reorder, hide and edit, plus the hero
slides at the top.
"""

from collections.abc import Callable
from typing import TYPE_CHECKING, ClassVar

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

from apps.core.models import BaseModel, ImageMixin, OrderableMixin, PublishableMixin
from apps.pages.paths import normalize_path

if TYPE_CHECKING:
    from django.db.models.fields.related_descriptors import RelatedManager


class Page(BaseModel, PublishableMixin):
    slug = models.SlugField(
        max_length=60, unique=True, help_text="Fixed: the code finds each page by it."
    )
    title = models.CharField(
        max_length=120, help_text="The page's name in the admin and the browser tab."
    )
    meta_title = models.CharField(
        "title in search results",
        max_length=70,
        blank=True,
        help_text="Shown as written (up to about 60 characters show in Google). Leave empty "
        "for “<page title> | Distinctive Consultancy Services”.",
    )
    meta_description = models.CharField(
        "description in search results",
        max_length=300,
        blank=True,
        help_text="One or two sentences. Leave empty to use the site's default.",
    )

    if TYPE_CHECKING:  # reverse relations Django adds; declared for the type checker only
        sections: RelatedManager["PageSection"]
        slides: RelatedManager["HeroSlide"]

    class Meta(BaseModel.Meta):  # pyright: ignore[reportIncompatibleVariableOverride]  # Meta of several abstract parents
        ordering: ClassVar = ["pk"]

    def __str__(self) -> str:
        return self.title


class PageSection(BaseModel, PublishableMixin, OrderableMixin, ImageMixin):
    """One block of a page. `section_type` picks how it looks (templates/includes/_section.html)."""

    image_upload_to = "pages/sections"

    class SectionType(models.TextChoices):
        HERO_TEXT = "hero_text", "Image band with a large heading"
        INTRO_DARK = "intro_dark", "Introduction on black"
        BAND_LIGHT = "band_light", "Band on white"
        BAND_DARK = "band_dark", "Band on dark grey"
        TWO_COLUMN = "two_column", "Two columns (short text left, long text right)"
        VALUE_BLOCK = "value_block", "Image beside heading and text"
        SERVICE_CARDS = "service_cards", "Service cards (the services ticked “show on Home”)"
        SERVICE_BANDS = "service_bands", "Every service, in alternating bands (Services page)"
        PARTNERS = "partners", "Strategic partners (logos)"
        CLIENTS = "clients", "Corporate clients (logos)"
        TEAM = "team", "Leadership team"
        CTA = "cta", "Call to action (a line and a button)"
        CONTACT_FORM = "contact_form", "Contact form beside “Reach Us” (Contact page)"
        ENQUIRY_FORM = "enquiry_form", "Enquiry form on gold (Services page)"
        MAP = "map", "Map (shown after the visitor accepts cookies)"

    class ImagePosition(models.TextChoices):
        LEFT = "left", "Left"
        RIGHT = "right", "Right"

    class Align(models.TextChoices):
        LEFT = "left", "Left"
        CENTER = "center", "Centre"
        RIGHT = "right", "Right"

    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="sections")
    if TYPE_CHECKING:  # attributes Django adds; declared for the type checker only
        page_id: int
        get_section_type_display: Callable[[], str]
    section_type = models.CharField("look", max_length=20, choices=SectionType.choices)
    eyebrow = models.CharField(
        "label",
        max_length=60,
        blank=True,
        help_text="A short label shown above the heading, such as “What we do”. Optional.",
    )
    heading = models.CharField(max_length=200, blank=True)
    heading_align = models.CharField(
        "heading position", max_length=6, choices=Align.choices, default=Align.LEFT
    )
    intro = models.TextField(
        "short text",
        blank=True,
        help_text="Two columns only: the short text under the heading on the left. Markdown.",
    )
    body = models.TextField(
        blank=True,
        help_text="Markdown: **bold**, *italic*, [link text](https://…), "
        "lists with - at the start of a line.",
    )
    image_position = models.CharField(
        max_length=5, choices=ImagePosition.choices, default=ImagePosition.LEFT
    )
    button_label = models.CharField(max_length=60, blank=True)
    button_url = models.CharField(
        "button link",
        max_length=200,
        blank=True,
        help_text="A page on this site (/contact/) or a full address (https://…).",
    )
    anchor = models.SlugField(
        max_length=80,
        blank=True,
        help_text="The #name other pages link to. Filled in from the heading if left empty, "
        "then kept, so links keep working if the heading changes.",
    )

    class Meta(OrderableMixin.Meta):  # pyright: ignore[reportIncompatibleVariableOverride]  # Meta of several abstract parents
        verbose_name = "section"
        constraints: ClassVar = [
            models.UniqueConstraint(
                fields=["page", "anchor"], name="pagesection_anchor_unique_per_page"
            ),
        ]

    def __str__(self) -> str:
        return self.heading or self.get_section_type_display()

    def save(self, *args, **kwargs):
        if not self.anchor:
            self.anchor = self._unique_anchor()
        super().save(*args, **kwargs)

    def _unique_anchor(self) -> str:
        base = slugify(self.heading)[:72] or self.section_type.replace("_", "-")
        candidate, n = base, 2
        siblings = type(self)._default_manager.filter(page_id=self.page_id).exclude(pk=self.pk)
        while siblings.filter(anchor=candidate).exists():
            candidate, n = f"{base}-{n}", n + 1
        return candidate


class Partner(BaseModel, PublishableMixin, OrderableMixin, ImageMixin):
    """A logo in a logo grid: a strategic partner (About) or a corporate client (Services)."""

    image_upload_to = "partners"

    class Kind(models.TextChoices):
        PARTNER = "partner", "Strategic partner"
        CLIENT = "client", "Corporate client"

    kind = models.CharField(max_length=10, choices=Kind.choices, default=Kind.PARTNER)
    name = models.CharField(max_length=120)
    caption = models.CharField(
        max_length=160, blank=True, help_text="Shown under the logo. Leave empty for none."
    )
    url = models.URLField("website", blank=True, help_text="The logo links here if filled in.")

    class Meta(OrderableMixin.Meta):  # pyright: ignore[reportIncompatibleVariableOverride]  # Meta of several abstract parents
        verbose_name = "partner or client"
        verbose_name_plural = "partners and clients"

    def __str__(self) -> str:
        return self.name


class HeroSlide(BaseModel, PublishableMixin, OrderableMixin, ImageMixin):
    """A slide in the image slider at the top of a page (Home). One slide shows without controls."""

    image_upload_to = "pages/slides"

    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="slides")
    heading = models.CharField(max_length=120)
    subheading = models.CharField(max_length=200, blank=True)
    button_label = models.CharField(max_length=60, blank=True)
    button_url = models.CharField("button link", max_length=200, blank=True)

    class Meta(OrderableMixin.Meta):  # pyright: ignore[reportIncompatibleVariableOverride]  # Meta of several abstract parents
        verbose_name = "hero slide"

    def __str__(self) -> str:
        return self.heading


class Redirect(BaseModel):
    """An old site address that now lives somewhere else (docs/architecture.md §7).

    RedirectMiddleware answers with it only when nothing else does (the request would be a 404),
    so a redirect can never hide a live page.
    """

    old_path = models.CharField(
        "old address",
        max_length=300,
        unique=True,
        help_text="The old site's address from the first slash, e.g. /about-us/. A full address "
        "(https://distinctive.co.zw/about-us/) is shortened to that when saved.",
    )
    new_path = models.CharField(
        "now at",
        max_length=300,
        help_text="A page on this site (/about/, /services/#hr-audits) or a full address.",
    )
    match_prefix = models.BooleanField(
        "and everything under it",
        default=False,
        help_text="Tick to also send every address that starts with the old one "
        "(/category/jobs/… as well as /category/jobs/).",
    )
    is_permanent = models.BooleanField(
        "permanent (301)",
        default=True,
        help_text="Untick for a temporary redirect (302), e.g. while a page is being rebuilt.",
    )
    is_active = models.BooleanField("active", default=True)
    note = models.CharField(max_length=200, blank=True)
    hits = models.PositiveIntegerField(default=0, editable=False)
    last_hit_at = models.DateTimeField("last used", null=True, blank=True, editable=False)

    class Meta(BaseModel.Meta):  # pyright: ignore[reportIncompatibleVariableOverride]  # Meta of an abstract parent
        ordering: ClassVar = ["old_path"]
        verbose_name = "redirect"

    def __str__(self) -> str:
        return f"{self.old_path} → {self.new_path}"

    def clean(self) -> None:
        super().clean()
        self.old_path = normalize_path(self.old_path)
        target = (self.new_path or "").strip()
        if not (target.startswith("/") or target.startswith(("http://", "https://"))):
            raise ValidationError(
                {"new_path": "Start with / for a page on this site, or https:// for another site."}
            )
        if target.startswith("/") and normalize_path(target.split("#")[0]) == self.old_path:
            raise ValidationError({"new_path": "This would send the address to itself."})
        self.new_path = target

    def save(self, *args, **kwargs):
        self.old_path = normalize_path(self.old_path)
        super().save(*args, **kwargs)
