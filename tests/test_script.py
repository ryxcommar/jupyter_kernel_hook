import os
import subprocess
from textwrap import dedent
from dataclasses import dataclass

import pytest
from jupyter_kernel_hook import _globals
from jupyter_kernel_hook import core
from jupyter_kernel_hook.core import ScriptInfo


def test_script_info_from_str():
    s = ScriptInfo.from_str("some_package")
    assert s.path == "some_package"
    assert s.obj is None

    s = ScriptInfo.from_str("some_package:some_function('foo')")
    assert s.path == "some_package"
    assert s.obj == "some_function('foo')"


def test_script_info_exists(ipython_scripts_dir):
    f = ipython_scripts_dir.join("/50-my_package.py")
    f.write_text("print('Hello, World!')", encoding="utf8")

    directory = ipython_scripts_dir.strpath

    assert ScriptInfo("my_package", None).exists(directory)
    assert not ScriptInfo("not_my_package", None).exists(directory)


@dataclass
class ScriptInfoCase:
    text: str
    script: str

    def __post_init__(self):
        self.script = dedent(self.script).strip()

    @property
    def obj(self):
        return ScriptInfo.from_str(self.text)


render_cases = [
    ScriptInfoCase(
        text="some_package",
        script="""
            import some_package  # noqa: F401
            """
    ),
    ScriptInfoCase(
        text="some_package:func()",
        script="""
            from some_package import func
            func()
            """
    ),
    ScriptInfoCase(
        text="some_package:func(a='apples')",
        script="""
            from some_package import func
            func(a='apples')
            """
    ),
    ScriptInfoCase(
        text="some_package:func(ip)",
        script="""
            from some_package import func
            from IPython import get_ipython
            ip = get_ipython()
            func(ip)
            """
    ),
    ScriptInfoCase(
        text="some_package:func(ip=ip)",
        script="""
            from some_package import func
            from IPython import get_ipython
            ip = get_ipython()
            func(ip=ip)
            """
    ),
    ScriptInfoCase(
        text="some_package:func(2, ip=ip, a='apples')",
        script="""
            from some_package import func
            from IPython import get_ipython
            ip = get_ipython()
            func(2, ip=ip, a='apples')
            """
    )
]


@pytest.mark.parametrize("script_info_case", render_cases)
def test_script_info_render(script_info_case):
    assert script_info_case.obj.render() == script_info_case.script


@pytest.mark.parametrize("script_info_case", render_cases)
def test_jinja_env_render(jinja_env, script_info_case):
    template = jinja_env.get_template("init.py.jinja")
    full_script = template.render(script_info=script_info_case.obj)

    for row in script_info_case.script.split("\n"):
        assert row.strip() in full_script


@pytest.mark.parametrize("script_info_case", render_cases)
@pytest.mark.parametrize("add_to_globals", [False, True])
def test_jinja_env_valid_py_file(script_info_case, add_to_globals,
                                 jinja_env, tmpdir):
    template = jinja_env.get_template("init.py.jinja")
    full_script = template.render(
        script_info=script_info_case.obj,
        add_to_globals=add_to_globals
    )

    directory = tmpdir.mkdir("scripts")
    f = directory.join("main.py")
    f.write_text(full_script, encoding="utf8")

    exit_code = subprocess.call(
        ["flake8", "--isolated", directory.strpath],
        # stdout=open(os.devnull, 'w')
    )

    assert exit_code == 0


@pytest.mark.parametrize("script_info_case", render_cases)
def test_core_main(nb_app, script_info_case,
                   ipython_scripts_dir, jinja_env):
    core.main(
        nb_app,
        script_info_case.text
    )

    filename = script_info_case.obj.gen_filename()
    f = ipython_scripts_dir.join(filename)

    assert f.exists()

    template = jinja_env.get_template("init.py.jinja")
    expected_contents = template.render(
        script_info=script_info_case.obj
    )
    actual_contents = f.read_text(encoding="utf8")

    assert actual_contents == expected_contents
