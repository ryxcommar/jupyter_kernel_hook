from unittest.mock import patch

import pytest

from jupyter_kernel_hook import _globals
from jupyter_kernel_hook import core


@pytest.fixture
def lazy_loader_patch(monkeypatch):
    monkeypatch.setitem(
        _globals._lazy_loaders,
        "foo",
        lambda: "bar"
    )


def test_lazy_load_getattr(lazy_loader_patch):
    """This test covers both the Python 3.6 case and the 3.7+ case in one go."""
    assert _globals.__getattr__("foo") == "bar"


def test_app_extensions(nb_app):
    assert core._app_enabled_extensions(nb_app, "fake_extension")
    assert not core._app_enabled_extensions(nb_app, "fake_fake_extension")
    assert not core._app_enabled_extensions(nb_app, "disabled_extension")
