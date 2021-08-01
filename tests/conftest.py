import sys
import json

import pytest
import jupyter_core.paths
from notebook.notebookapp import NotebookApp

from jupyter_kernel_hook import _globals
from jupyter_kernel_hook.core import jupyter_config_json


IS_PY36 = sys.version_info.major == 3 and sys.version_info.minor == 6


def _delete_global(s: str):
    try:
        delattr(_globals, s)
    except AttributeError:
        pass


@pytest.fixture(autouse=True)
def reset_lazy_loads():
    yield
    _delete_global("jinja_env")
    _delete_global("startup_dir")
    _delete_global("enabled_server_extensions")


@pytest.fixture
def ipython_scripts_dir(tmpdir):
    directory = tmpdir.mkdir("startup")
    yield directory


@pytest.fixture(autouse=True)
def mock_scripts_dir(monkeypatch, ipython_scripts_dir):
    if IS_PY36:
        _globals.startup_dir = None
    monkeypatch.setattr(
        _globals,
        "startup_dir",
        ipython_scripts_dir.strpath,
    )
    yield


@pytest.fixture
def jupyter_config_dir(tmpdir):
    directory = tmpdir.mkdir("jupyter_config")

    # Enable a fake package.
    d = jupyter_config_json("fake_extension")
    cfg_file = directory.join("/jupyter_notebook_config.json")
    cfg_file.write_text(json.dumps(d), encoding="utf8")

    yield directory


@pytest.fixture(autouse=True)
def jupyter_config_path_func(monkeypatch, jupyter_config_dir):
    monkeypatch.setattr(
        jupyter_core.paths,
        "jupyter_config_path",
        lambda: [jupyter_config_dir.strpath]
    )
    yield


@pytest.fixture
def nb_app(jupyter_config_dir):
    yield NotebookApp(
        nbserver_extensions={
            "fake_extension": True,
            "disabled_extension": False
        }
    )


@pytest.fixture
def jinja_env():
    yield _globals.__getattr__("jinja_env")
