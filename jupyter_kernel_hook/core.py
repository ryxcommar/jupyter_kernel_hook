import os
import re
import ast
import glob
import typing as t
from dataclasses import dataclass

from notebook.notebookapp import NotebookApp

from . import _globals


def _find_arg(s: t.Optional[str], arg_names: t.List[str]) -> bool:
    if s is None:
        return False
    expr = ast.parse(s, mode="eval").body
    if isinstance(expr, ast.Call):
        for arg in expr.args:
            if isinstance(arg, ast.Name):
                if arg.id in arg_names:
                    return True
        for kwarg in expr.keywords:
            for i in arg_names:
                if isinstance(kwarg.value, ast.Name):
                    if kwarg.arg == kwarg.value.id == i:
                        return True
    return False


@dataclass
class ScriptInfo(object):
    path: str
    obj: t.Optional[str] = None

    @property
    def uses_ipy(self) -> bool:
        return _find_arg(self.obj, ["ip", "ipy", "ipython"])

    @property
    def is_called(self) -> bool:
        expr = ast.parse(self.obj, mode="eval").body
        return isinstance(expr, ast.Call)

    @property
    def obj_name(self) -> str:
        expr = ast.parse(self.obj, mode="eval").body
        if isinstance(expr, ast.Name):
            return expr.id
        elif isinstance(expr, ast.Call):
            return expr.func.id
        else:
            return self.obj

    @property
    def filename_base(self):
        return self.path.replace('.', '-')

    @property
    def _filename(self) -> str:
        return "{priority}-" + self.filename_base + ".py"

    def gen_filename(self, priority: int = 50) -> str:
        return self._filename.format(priority=str(priority).zfill(2))

    def exists(self, startup_dir: str) -> bool:
        match_me = self._filename.format(priority="")
        return len(glob.glob(f"{startup_dir}/*{match_me}")) > 0

    def render(self, add_to_globals: bool = False) -> str:
        if self.obj is None:
            if add_to_globals:
                s = f"import {self.path}\n"
                s += f"globals()['{self.path}'] = {self.path}"
                return s
            else:
                return f"import {self.path}  # noqa: F401"
        elif not self.is_called:
            return f"from {self.path} import {self.obj_name}"
        else:
            li = [f"from {self.path} import {self.obj_name}"]
            if self.uses_ipy:
                li.append("from IPython import get_ipython")
                li.append("ip = get_ipython()")
            li.append(self.obj)
            if add_to_globals:
                li.append(f"import {self.path}")
                li.append(f"globals()['{self.path}'] = {self.path}")
            return "\n".join(li)

    @classmethod
    def from_str(cls, o: str):
        path, obj = [*re.split(r":(?![\\/])", o, 1), None][:2]
        if obj is not None:
            obj = obj.strip()
        return cls(path=path, obj=obj)


ScriptInfoType = t.TypeVar("ScriptInfoType", ScriptInfo, str)


def jupyter_config_json(
        package_name: str,
        enabled: bool = True
) -> dict:
    """Creates a Jupyter Config JSON file with one package defined."""
    return {
        "NotebookApp": {
            "nbserver_extensions": {
                package_name: enabled
            }
        }
    }


def _app_enabled_extensions(nb_app: NotebookApp, path: str) -> bool:
    enabled = nb_app.nbserver_extensions.get(path)
    if enabled is None:
        nb_app.log.info(f"Extension {path!r} not installed.")
        return False
    elif enabled is False:
        nb_app.log.info(f"Extension {path!r} not enabled.")
        return False
    else:
        nb_app.log.info(f"Extension {path!r} enabled.")
        return True


def main(
        nb_app: NotebookApp,
        script_info: ScriptInfoType,
        priority: int = 50,
        overwrite: bool = False,
        add_to_globals: bool = False
) -> None:
    """Create startup script."""
    # Format into a ScriptInfo object.
    priority = int(priority)
    assert 0 <= priority <= 99, "priority must be between 0 and 99"

    if isinstance(script_info, str):
        script_info = ScriptInfo.from_str(script_info)

    # Check if the extension is enabled.
    #
    # Usually when this function is called, it's because the extension was
    # already enabled. This is just a safeguard against unintended behavior.
    # It's good to be cautious when editing a user's file system.

    if not _app_enabled_extensions(nb_app, script_info.path):
        return

    # Now we've established that the extension is enabled.
    # Let's see if we need to write the script or not.

    startup_dir = _globals.__getattr__("startup_dir")

    # See if the script exists.
    # If it does, stop running this.
    if script_info.exists(startup_dir=startup_dir) and not overwrite:
        return

    jinja_env = _globals.__getattr__("jinja_env")

    script = jinja_env \
        .get_template("init.py.jinja") \
        .render(
            script_info=script_info,
            add_to_globals=add_to_globals)

    filename = script_info.gen_filename(priority=priority)
    destination = os.path.join(startup_dir, filename)

    # Write the script to the startup_dir:
    with open(destination, "w+") as f:
        f.write(script)

    nb_app.log.info(f"Created new startup script: {destination!r}.")
    return
