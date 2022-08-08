# Plugin Template

Plugins are features that extend Manim's core functionality. This is a
template project that demonstrates how you can create and upload a manim
plugin to PyPI using a PEP 517 compliant build system,
[Poetry](https://python-poetry.org).

Poetry is **NOT** required to create plugins, but is recommended because
it provides build isolation and ensures users can reliably install your
plugin without falling into dependency hell. You may use another build
system (e.g. Flit, Setuptools, Pipenv, etc...) if you wish.

# Plugin Website

A gallery of current plugins can be found here: https://plugins.manim.community/

## Creating Plugins

The only requirement of your preferred build system is that it specifies
the `manim.plugins` [entry
point](https://packaging.python.org/specifications/entry-points/).

> **note**
>
> The plugin naming convention is to add the prefix `manim-`. This
> allows users to easily search for plugins on organizations like PyPi,
> but it is not required.

### Installing Poetry

Poetry can be installed on Windows, MacOS and Linux. Please visit the
official poetry website for [installation
instructions](https://python-poetry.org/docs/#installation). You may
want to see the official documentation for a list of all [available
commands](https://python-poetry.org/docs/cli/).

### Setting Up Your Plugin Directory Structure

To create a Python project suitable for poetry, run:

``` {.sourceCode .bash}
poetry new --src manim-YourPluginName 
```

> **note**
>
> `--src` is both optional and recomended in order to create a src
> directory where all of your plugin code should live.

This will create the following project structure: :

    manim-YourPluginName
    ├── pyproject.toml
    ├── README.rst
    ├── src
    │   └── manim_yourpluginname
    │       └── __init__.py
    └── tests
        ├── __init__.py
        └── test_manim_yourpluginname.py 

If you have already extended manim's functionality, you can instead run:

``` {.sourceCode .bash}
cd path/to/plugin
poetry init
```

This will prompt you for basic information regarding your plugin and
help create and populate a `pyproject.toml` similar to the one in this
template; however, you may wish to update your project directory
structure similarly.

See the official documentation for more information on the [init
command](https://python-poetry.org/docs/cli/#init).

From now on, when working on your plugin, ensure you are using the
virtual environment by running the following at the root of your
project:

``` {.sourceCode .bash}
poetry shell 
```

### Updating Pyproject.toml

The `pyproject.toml` file is used by Poetry and other build systems to
manage and configure your project. Manim uses the package's entry point
metadata to discover available plugins. The entry point group,
`"manim.plugins"`, is **REQUIRED** and can be [specified as
follows](https://python-poetry.org/docs/pyproject/#plugins):

``` {.sourceCode .toml}
[tool.poetry.plugins."manim.plugins"]
"manim_yourpluginname" = "module:object.attr"
```

> **note**
>
> The left hand side represents the entry point name which should be
> unique among other plugin names. This is the internal name Manim will
> use to identify and handle plugins.
>
> The right hand side should reference a python object (i.e. module,
> class, function, method, etc...) and will be the first code run in
> your plugin. In the case of this template repository, the package name
> is used which Python interprets as the package's `__init__.py` module.
>
> See the python packaging
> [documentation](https://packaging.python.org/specifications/entry-points/)
> for more information on entry points.

### Testing Your Plugin Locally


``` {.sourceCode .bash}
poetry install
```

This command will read the `pyproject.toml`, install the dependencies of
your plugin, and create a `poetry.lock` file to ensure everyone using
your plugin gets the same version of dependencies. It is important that
your dependencies are properly annotated with a version constraint (e.g.
`manim:^0.1.1`, `numpy:*`, etc...). Equally important to the
dependencies specified here is that they do not directly conflict with
[Manim's](https://github.com/ManimCommunity/manim/blob/master/pyproject.toml).
If you want to update the dependencies specified in `pyproject.toml`,
use:

``` {.sourceCode .bash}
poetry update
```

See the official documentation for more information on
[versioning](https://python-poetry.org/docs/dependency-specification/)
or the [install command](https://python-poetry.org/docs/cli/#install).

Poetry allows for dependencies that are strictly for project developers.
These are not installed by users. To add them to your project, update
the `pyproject.toml` file with the section followed by the dependencies:

``` {.sourceCode .toml}
[tool.poetry.dev-dependencies]
pytest = "*"
pylint = "*"
```

The `pytest` package is a functional testing framework which you can use
to run the test within the `manim-YourPluginName/tests` directory. You
should create files which test the behavior and functionality of your
plugin here. Test first development is a good practice to ensure your
code behaves as intended before packaging and shipping your code
publicly. Additionally, you can create Manimations that depend on your
plugin which is another great way to ensure functionality.

### Uploading Your Project


By default, poetry is set to register the package/plugin to PyPI. You'll
need to register an account there to upload/update your plugin. As soon
as your plugin is useful locally, run the following:

``` {.sourceCode .bash}
poetry publish --build
```

Your project should now be available on PyPI for users to install via
`pip install manim-YourPluginName` and usable within their respective
environments.

See the official documentation for more information on the [publish
command](https://python-poetry.org/docs/cli/#publish).

## Code of Conduct


Our full code of conduct, and how we enforce it, can be read on [our website](https://docs.manim.community/en/latest/conduct.html).
