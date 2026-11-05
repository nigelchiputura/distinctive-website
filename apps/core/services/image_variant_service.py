"""Smaller WebP copies of uploaded images, so phones don't download the full-size file
(docs/frontend.md §6).

`srcset(obj)` returns a `srcset` value for an ImageMixin object: a WebP copy at each width in
WIDTHS that is narrower than the original, then the original itself. Copies are made the first
time a page needs them and kept under `media/variants/<width>/`, so later requests only check
that they exist. A new upload has a new file name, so its copies are made afresh. Any failure
(a missing or unreadable file) is logged and leaves the plain `src` to do the job.
"""

import logging
from io import BytesIO
from pathlib import PurePosixPath
from typing import Any

from django.core.files.base import ContentFile
from django.core.files.storage import Storage, default_storage
from PIL import Image, ImageOps

from apps.core.services.base import BaseService

logger = logging.getLogger(__name__)

WIDTHS = (480, 800, 1200, 1600, 2000)
QUALITY = 78


class ImageVariantService(BaseService):
    def __init__(self, storage: Storage | None = None, widths: tuple[int, ...] = WIDTHS):
        self.storage = storage or default_storage
        self.widths = widths

    @staticmethod
    def variant_name(name: str, width: int) -> str:
        return str(
            PurePosixPath("variants") / str(width) / PurePosixPath(name).with_suffix(".webp")
        )

    def srcset(self, obj: Any) -> str:
        field = getattr(obj, "image", None)
        width = getattr(obj, "image_width", None)
        if not field or not width:
            return ""
        try:
            entries = [
                f"{self.storage.url(self._ensure(field.name, w))} {w}w"
                for w in self.widths
                if w < width
            ]
        except Exception as exc:  # a missing or unreadable upload: the plain src still works
            logger.warning("No smaller copies of %s: %s", field.name, exc)
            return ""
        if not entries:
            return ""
        entries.append(f"{field.url} {width}w")
        return ", ".join(entries)

    def _ensure(self, name: str, width: int) -> str:
        target = self.variant_name(name, width)
        if self.storage.exists(target):
            return target
        with self.storage.open(name, "rb") as source:
            image = ImageOps.exif_transpose(Image.open(source))
            image = image.convert("RGBA" if image.mode in ("RGBA", "LA", "P") else "RGB")
            height = round(image.height * width / image.width)
            image = image.resize((width, height), Image.Resampling.LANCZOS)
            buffer = BytesIO()
            image.save(buffer, "WEBP", quality=QUALITY, method=4)
        # Two workers can race to make the same copy; storage then picks another name for the
        # second, which is still a correct copy, so use whatever name it returns.
        return self.storage.save(target, ContentFile(buffer.getvalue()))
