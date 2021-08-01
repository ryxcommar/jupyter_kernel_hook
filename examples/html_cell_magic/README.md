# HTML Cell Magic (Jupyter Kernel Hook demo)

This demo extension renders HTML into cells using cell magic. It's not particularly useful because markdown cells also render HTML. But it is simple enough to implement and understand, so it makes for a compelling demo.

## How to run demo:

1. `cd` to this directory.

2. Run the following:
    * OSX/Linux:
        ```shell
        python3 -m venv venv
        source venv/bin/activate
        pip install -e .
        jupyter notebook
        ```
    * Windows (CMD):
        ```shell
        python3 -m venv venv
        venv\Scripts\activate.bat
        pip install -e .
        jupyter notebook
        ```

3. Pip editable installs [have a dumb problem with data files](https://github.com/pypa/pip/issues/6592). (For PyPi installs, this issue doesn't exist.) You will need to manually move the `html_cell_magic_jupyter_config.json` into the appropriate folder. Use the following to do that:

```shell
destpath=venv/etc/jupyter/jupyter_notebook_config.d
mkdir -p "$destpath"
cp html_cell_magic/html_cell_magic_jupyter_config.json "$destpath"
```

4. You may need to restart your terminal before running the `jupyter notebook` command to have everything register OK. So for best results, exit the terminal, open a new one, `cd` back to this directory, and `source venv/bin/activate` again.

5. Run `jupyter notebook`.

6. Open up the `demo.ipynb` notebook.

7. Run the notebook! If everything was done properly, the notebook should run.
