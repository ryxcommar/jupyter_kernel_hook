# flake8: noqa: F821
"""Lazy loaded globals. Sadly they must be eagerly loaded in Python 3.6."""
import os
import sys
import typing as t


# Eager loaded attributes
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")


# Lazy loaded attributes
jinja_env: "jinja2.Environment"
startup_dir: str
enabled_server_extensions: t.Set[str]


def _get_jinja_env() -> "jinja2.Environment":
    import jinja2
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(TEMPLATES_DIR),
        keep_trailing_newline=True
    )


def _get_startup_dir() -> str:
    from IPython.paths import get_ipython_dir
    from IPython.core.profiledir import ProfileDir

    print(get_ipython_dir())
    import glob
    print(glob.glob(get_ipython_dir() + '*'))

    profile_dir = ProfileDir.find_profile_dir_by_name(
        get_ipython_dir(),
        "default"
    )
    return profile_dir.startup_dir


def _get_enabled_server_extensions() -> t.Set[str]:
    from notebook.config_manager import BaseJSONConfigManager
    from jupyter_core.paths import jupyter_config_path

    s = set()
    config_dirs = jupyter_config_path()
    for config_dir in config_dirs:
        cm = BaseJSONConfigManager(config_dir=config_dir)
        data = cm.get("jupyter_notebook_config")
        server_extensions = (
            data.setdefault("NotebookApp", {})
                .setdefault("nbserver_extensions", {})
        )
        for k, v in server_extensions.items():
            if v:
                s.add(k)
    return s


def _load(s: str, callback: callable) -> t.Any:
    try:
        o = globals()[s]
    except KeyError:
        o = callback()
        globals()[s] = o
        return o
    else:
        return o


_lazy_loaders = {
    "jinja_env": _get_jinja_env,
    "startup_dir": _get_startup_dir,
    "enabled_server_extensions": _get_enabled_server_extensions
}


def __getattr__(s: str):
    """This only works in Python 3.7+."""
    try:
        callback = _lazy_loaders[s]
    except KeyError:
        raise AttributeError(f"{__name__!r} object has no attribute {s!r}")
    else:
        return _load(s, callback)


__all__ = [
    "TEMPLATES_DIR",
    "jinja_env",
    "startup_dir",
    "enabled_server_extensions"
]
