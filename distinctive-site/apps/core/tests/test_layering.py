"""The architecture rule as a CI rule (docs/architecture.md §2):

- controllers never import a repository or the ORM (`django.db`);
- services never call `Model.objects`.

`find_violations` works on source text, so the rule itself is tested with deliberately bad
snippets as well as run over the real code.
"""

import ast
from pathlib import Path

import pytest
from django.conf import settings

APPS_DIR = Path(settings.BASE_DIR) / "apps"


def _imported_modules(tree: ast.AST) -> list[str]:
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = "." * node.level + (node.module or "")
            names.append(module)
            names.extend(f"{module}.{alias.name}" for alias in node.names)
    return names


def find_violations(layer: str, source: str) -> list[str]:
    """Rule breaks in one file's `source`, for a file in `layer` ("controllers" | "services")."""
    tree = ast.parse(source)
    problems: list[str] = []
    if layer == "controllers":
        for name in _imported_modules(tree):
            parts = name.lstrip(".").split(".")
            if "repositories" in parts:
                problems.append(f"imports a repository ({name})")
            if name.lstrip(".").startswith("django.db"):
                problems.append(f"imports the ORM ({name})")
    if layer in ("controllers", "services"):
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr == "objects":
                problems.append(f"uses .objects (line {node.lineno})")
    return problems


def _layer_files(layer: str) -> list[Path]:
    return sorted(p for p in APPS_DIR.glob(f"*/{layer}/*.py") if p.name != "__init__.py")


@pytest.mark.parametrize("layer", ["controllers", "services"])
def test_the_real_code_follows_the_layering(layer):
    files = _layer_files(layer)
    assert files, f"no {layer} found: has the folder layout changed?"
    report = {
        str(path.relative_to(APPS_DIR)): problems
        for path in files
        if (problems := find_violations(layer, path.read_text()))
    }
    assert report == {}, f"Layering broken (docs/architecture.md §2): {report}"


@pytest.mark.parametrize(
    "source",
    [
        "from apps.pages.repositories.page_repository import PageRepository",
        "from ..repositories import page_repository",
        "import apps.pages.repositories.page_repository",
        "from django.db import models",
        "from django.db.models import Q",
        "def get(self):\n    return Page.objects.all()",
    ],
)
def test_a_controller_breaking_the_rule_is_caught(source):
    assert find_violations("controllers", source)


def test_a_service_calling_objects_is_caught():
    assert find_violations("services", "def f():\n    return Page.objects.filter(x=1)")


@pytest.mark.parametrize(
    "source",
    [
        "from apps.pages.services.page_service import PageService",
        "from django.http import HttpResponse",
        "from django.views import View",
    ],
)
def test_a_controller_following_the_rule_passes(source):
    assert find_violations("controllers", source) == []


def test_a_service_may_import_its_repository():
    source = "from apps.pages.repositories.page_repository import PageRepository"
    assert find_violations("services", source) == []
