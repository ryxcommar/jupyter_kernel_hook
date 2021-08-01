from IPython.core.magic import Magics, magics_class, cell_magic
from IPython.core.interactiveshell import InteractiveShell
from IPython.core.display import display, HTML


@magics_class
class HtmlMagics(Magics):

    @cell_magic
    def html(self, line, cell):
        return display(HTML(cell))  # noqa


def _jupyter_server_extension_paths():
    return [{
        "module": "html_cell_magic"
    }]


def load_jupyter_server_extension(nb_app):
    from jupyter_kernel_hook import create_startup_script
    create_startup_script(
        nb_app,
        "html_cell_magic:load_ipython_extension(ip)"
    )


def load_ipython_extension(ip: InteractiveShell):
    ip.register_magics(HtmlMagics)
