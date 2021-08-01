"""Test everything in ``jupyter_kernel_hook/__init__.py``. """
import pytest
from unittest.mock import patch

import jupyter_kernel_hook
from jupyter_kernel_hook import core


@pytest.fixture
def core_main():
    with patch.object(core, "main") as f:
        yield f


def test_create_startup_script(core_main, nb_app):
    """Check that `create_startup_script` properly calls ``core.main``."""

    args = (nb_app, "foo")
    kwargs = dict(priority=42, overwrite=True, add_to_globals=True)
    jupyter_kernel_hook.create_startup_script(*args, **kwargs)

    # We should have passed everything directly to `core.main()`
    core_main.assert_called_once_with(*args, **kwargs)


def test_extension_is_enabled():
    # This extension exists (it's created in the jupyter_config_dir fixture)
    assert jupyter_kernel_hook.extension_is_enabled("fake_extension")

    # This extension does *not* exist.
    assert not jupyter_kernel_hook.extension_is_enabled("fake_fake_extension")
