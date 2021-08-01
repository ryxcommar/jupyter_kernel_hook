# Jupyter Kernel Hook

[![](https://github.com/ryxcommar/jupyter_kernel_hook/actions/workflows/tests.yml/badge.svg)](../../actions)
[![](https://github.com/ryxcommar/jupyter_kernel_hook/actions/workflows/style.yml/badge.svg)](../../actions)

A simple way to turn your package into a Jupyter server extension that automatically preload into an IPython kernel.

You can install this package via `pip install jupyter-kernel-hook`.

## Example

Add the following to your package's `__init__.py`:

```python
# my_package/__init__.py
def _jupyter_server_extension_paths():
    return [{
        "module": "my_package"
    }]


def load_jupyter_server_extension(nb_app):
    from jupyter_kernel_hook import create_startup_script
    create_startup_script(
        nb_app,
        "my_package"
    )
```

Now when a user runs `jupyter serverextension enable --py my_package`, your package will be enabled as a server extension that is preloaded within every IPython kernel.  So now the user does not need to run `import my_package` to run it for each kernel session.

## Features

* **Simplicity.** `jupyter_kernel_hook` does for you the annoying part of preloading your packages in a sane way.
* **Intuitive behavior.** Your startup script can be enabled and disabled through `jupyter serverextension enable --py my_package`.
  * When your extension is **enabled**, it will preload (and invoke an optional function call) in each IPython kernel.
  * When your extension is **disabled**, it is never preloaded / imported.
* **Performance.** Everything is lazy-loaded to reduce overhead and required dependencies. (`jupyter_kernel_hook` is imported in various contexts-- the server starting up, kernels starting up-- and different contexts require different things.)

## Advanced

### Preload IPython Extension

Jupyter Kernel Hook is used to make Jupyter server extensions. A natural use case, though, is to turn a native [IPython extension](https://ipython.readthedocs.io/en/stable/config/extensions/index.html) into a Jupyter Notebook extension, such as those that add cell magic to the IPython runtime.

You can call a `load_ipython_extension` function like this:

```python
# my_package/__init__.py
from .core import MyPackageMagics

def _jupyter_server_extension_paths():
    return [{
        "module": "my_package"
    }]

def load_jupyter_server_extension(nb_app):
    from jupyter_kernel_hook import create_startup_script
    create_startup_script(
        nb_app,
        "my_package:load_ipython_extension(ip)"
    )

def load_ipython_extension(ip):
    ip.register_magics(MyPackageMagics)
```

And the startup script will make sure that the `ip` object is defined.

(Note: You can run any arbitrary function call, not just `load_ipython_extension`.)

### Add Package to Kernel's Global Namespace

By default, the global namespace of the IPython kernel is untouched by the generated script.

You can, however, add the package to the global namespace like this:

```python
create_startup_script(
    nb_app,
    "my_package:load_ipython_extension(ip)",
    add_to_globals=True
)
```

In this case, `my_package` will be available in the IPython kernel's globals.

(Warning: This doesn't work for nested packages/modules at the moment. Do that at your own risk.)

### Jupyter Entry Point in `Setup.py`

This is a Jupyter thing in general, but it's quite handy for your packages.

Basically you can make it so your package, when installed, automatically enables the server extension. In conjunction with Jupyter Kernel Hook, this means your IPython extensions are automatically enabled with just a pip install!

Read more about this in the official [Jupyter Notebook documentation](https://jupyter-notebook.readthedocs.io/en/stable/examples/Notebook/Distributing%20Jupyter%20Extensions%20as%20Python%20Packages.html).

#### `my_package/__init__.py`:

_(See above examples.)_

#### `setup.py`:

```python
from setuptools import setup

# ...

setup(
    # ...
    install_requires=[
        # ...
        "jupyter-kernel-hook"
    ],
    # ...
    include_package_data=True,
    data_files=[
        ("etc/jupyter/jupyter_notebook_config.d", [
            "my_package_jupyter/my_package_jupyter_config.json"
        ])
    ],
    zip_safe=False
    # ...
)
```

#### `my_package/my_package_jupyter_config.json`:

```json
{
  "NotebookApp": {
    "nbserver_extensions": {
      "my_package": true
    }
  }
}
```

#### `MANIFEST.in`:

```text
include my_package/my_package_jupyter_config.json
```

## The Spider-Man Rule

> With great power comes great responsibility.

The power to preload packages into IPython kernels is powerful and convenient at times, but it's also extremely easy to abuse.

It is recommended that you be very judicious about whether your package should have this behavior.

In general, merely wanting to make a package available in the global namespace is probably **not** a good reason to have your package preload into a kernel.  Extending the behavior of the kernel (e.g. cell magic) or packages run within it (e.g. Pandas extensions) are better reasons for having this behavior.
