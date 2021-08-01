from setuptools import setup


setup(
    name="html_cell_magic",
    python_requires=">=3.6",
    description="Demo for Jupyter Kernel Hook.",
    packages=["html_cell_magic"],
    include_package_data=True,
    install_requires=[
        "IPython",
        "notebook"
    ],
    # Note: for editable install:
    # destpath=venv/etc/jupyter/jupyter_notebook_config.d
    # mkdir -p "$destpath"
    # cp html_cell_magic/html_cell_magic_jupyter_config.json "$destpath"
    data_files=[
        ("etc/jupyter/jupyter_notebook_config.d", [
            "html_cell_magic/html_cell_magic_jupyter_config.json"
        ])
    ],
    zip_safe=False
)
