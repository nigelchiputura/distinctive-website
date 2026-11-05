"""ImageVariantService: smaller WebP copies for srcset."""

from io import BytesIO
from types import SimpleNamespace

import pytest
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from PIL import Image

from apps.core.services.image_variant_service import ImageVariantService


@pytest.fixture
def storage(tmp_path):
    return FileSystemStorage(location=tmp_path, base_url="/media/")


def upload(storage, name="pages/slides/team.jpg", size=(1300, 650), mode="RGB"):
    buffer = BytesIO()
    colour = (212, 175, 55, 0) if mode == "RGBA" else "gold"  # see-through, for the logo test
    Image.new(mode, size, colour).save(buffer, "PNG" if mode == "RGBA" else "JPEG")
    saved = storage.save(name, ContentFile(buffer.getvalue()))
    field = SimpleNamespace(name=saved, url=storage.url(saved))
    return SimpleNamespace(image=field, image_width=size[0], image_height=size[1])


def test_copies_narrower_than_the_original_then_the_original(storage):
    obj = upload(storage)
    srcset = ImageVariantService(storage).srcset(obj)
    assert srcset == (
        "/media/variants/480/pages/slides/team.webp 480w, "
        "/media/variants/800/pages/slides/team.webp 800w, "
        "/media/variants/1200/pages/slides/team.webp 1200w, "
        "/media/pages/slides/team.jpg 1300w"
    )
    with Image.open(storage.path("variants/800/pages/slides/team.webp")) as copy:
        assert copy.format == "WEBP" and copy.size == (800, 400)


def test_copies_are_made_once(storage, monkeypatch):
    obj = upload(storage)
    service = ImageVariantService(storage)
    service.srcset(obj)
    monkeypatch.setattr(storage, "save", lambda *a, **k: pytest.fail("made again"))
    assert "800w" in service.srcset(obj)


def test_transparency_is_kept(storage):
    obj = upload(storage, name="partners/logo.png", size=(900, 300), mode="RGBA")
    ImageVariantService(storage).srcset(obj)
    with Image.open(storage.path("variants/480/partners/logo.webp")) as copy:
        assert copy.mode == "RGBA"


def test_nothing_for_small_images_or_no_image(storage):
    service = ImageVariantService(storage)
    assert service.srcset(upload(storage, size=(400, 300))) == ""
    assert service.srcset(SimpleNamespace(image=None, image_width=None)) == ""


def test_a_missing_file_is_logged_and_skipped(storage, caplog):
    obj = SimpleNamespace(
        image=SimpleNamespace(name="gone.jpg", url="/media/gone.jpg"), image_width=2000
    )
    assert ImageVariantService(storage).srcset(obj) == ""
    assert "No smaller copies of gone.jpg" in caplog.text
