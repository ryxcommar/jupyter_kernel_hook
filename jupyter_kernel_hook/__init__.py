# flake8: noqa: F401
__version__ = "0.1.1"


def create_startup_script(
        nb_app: "notebook.notebookapp.NotebookApp",
        script_info: str,
        priority: int = 50,
        overwrite: bool = False,
        add_to_globals: bool = False
) -> None:
    """Create IPython startup script for your module.

    Args:
        nb_app: Active NotebookApp instance.
        script_info: Module in the form ``path.to.module``. You may also define
            an optional callable: ``path.to.module:function()``. You can pass
            the IPython instance as an argument ``ip``. This is usually used to
            run ``load_ipython_extension()``. For example:
            ``path.to.module:load_ipython_extension(ip)``.
        priority: The prefix to the startup script file that's created.
            Generally you should keep this at 50 unless you have a good reason.
        overwrite: Whether to overwrite the startup script file if it exists.
            By default this is turned off.
        add_to_globals: If True, add the imported package to the global
            namespace of the IPython kernel on load.
    """
    # Lazy load core module to reduce unnecessary overhead.
    # The only time this script ever needs to run is when firing up Jupyter.
    #
    # This is not a substitute for lazy-loading ``jupyter_kernal_hook`` in your
    # own packages, but some people won't read this comment, and we don't want
    # to hurt the users of their packages with lower performance.
    from .core import main
    return main(
        nb_app,
        script_info,
        priority=priority,
        overwrite=overwrite,
        add_to_globals=add_to_globals
    )


def extension_is_enabled(ext: str) -> bool:
    """Check to see whether a serverextension is enabled without requiring the
    NotebookApp instance. Typically what you'd do is look at
    ``nb_app.nbserver_extensions``. But we don't have the easiest access to
    that object in the IPython startup script context. So this script
    reimplements that logic.

    Lazy-loading ``enabled_server_extensions`` from ``_globals`` causes it to
    run the Notebook app config logic.

    Args:
        ext: Name of a Jupyter server extension.

    Returns:
        Boolean indicating whether the input extension name is enabled.
    """
    from . import _globals
    li = _globals.__getattr__("enabled_server_extensions")
    return bool(ext in li)


__all__ = [
    "create_startup_script",
    "extension_is_enabled",
    "__version__"
]
