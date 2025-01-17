# Project file syntax

## Project metadata

PDM reads the project's metadata following the standardized format of [PEP 621](https://www.python.org/dev/peps/pep-0621/).
View the PEP for the detailed specification. These metadata are stored in `[project]` table of `pyproject.toml`.

_In the following part of this document, metadata should be written under `[project]` table if not given explicitly._

### Determine the package version dynamically

You can specify a file source for `version` field like: `version = {from = "pdm/__init__.py"}`, in this form,
the version will be read from the `__version__` variable in that file.

PDM can also read version from SCM tags. If you are using git or hg as the version control system, define the
`version` as follows:

```toml
version = {use_scm = true}
```

In either case, you MUST also include `version` in `dynamic` field, or the backend will raise an error:

```toml
dynamic = ["version"]
```

### Dependency specification

The `project.dependencies` is an array of dependency specification strings following the [PEP 440](https://www.python.org/dev/peps/pep-0440/)
and [PEP 508](https://www.python.org/dev/peps/pep-0508/).

Examples:

```toml
dependencies = [
    # Named requirement
    "requests",
    # Named requirement with version specifier
    "flask >= 1.1.0",
    # Requirement with environment marker
    "pywin32; sys_platform == 'win32'",
    # URL requirement
    "pip @ https://github.com/pypa/pip.git@20.3.1"
]
```

### Editable requirement

Beside of the normal dependency specifications, one can also have some packages installed in editable mode. The editable specification string format
is the same as [Pip's editable install mode](https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs).

Examples:

```
dependencies = [
    ...,
    "-e path/to/SomeProject",
    "-e git+http://repo/my_project.git#egg=SomeProject"
]
```

!!! note "About editable installation"
    One can have editable installation and normal installation for the same package. The one that comes at last wins.
    However, editable dependencies WON'T be included in the metadata of the built artifacts since they are not valid
    PEP 508 strings. They only exist for development purpose.

### Optional dependencies

You can have some requirements optional, which is similar to `setuptools`' `extras_require` parameter.

```toml
[project.optional-dependencies]
socks = [ 'PySocks >= 1.5.6, != 1.5.7, < 2' ]
tests = [
  'ddt >= 1.2.2, < 2',
  'pytest < 6',
  'mock >= 1.0.1, < 4; python_version < "3.4"',
]
```

To install a group of optional dependencies:

```bash
$ pdm install -s socks
```

`-s` option can be given multiple times to include more than one group.

### Console scripts

The following content:

```toml
[project.scripts]
mycli = "mycli.__main__:main"
```

will be translated to `setuptools` style:

```python
entry_points = {
    'console_scripts': [
        'mycli=mycli.__main__:main'
    ]
}
```

Also, `[project.gui-scripts]` will be translated to `gui_scripts` entry points group in `setuptools` style.

### Entry points

Other types of entry points are given by `[project.entry-points.<type>]` section, with the same
format of `[project.scripts]`:

```toml
[project.entry-points.pytest11]
myplugin = "mypackage.plugin:pytest_plugin"
```

## PDM specific settings

There are also some useful settings that should be shipped with `pyproject.toml`. These settings are defined in `[tool.pdm]` table.

### Development dependencies

You can have several groups of development only dependencies. Unlike `optional-dependencies`, they won't appear in the package distribution metadata such as `PKG-INFO` or `METADATA`.
And the package index won't be aware of these dependencies. The schema is similar to that of `optional-dependencies`, except that it is in `tool.pdm` table.

```toml
[tool.pdm.dev-dependencies]
lint = [
    "flake8",
    "black"
]
test = ["pytest", "pytest-cov]
doc = ["mkdocs"]
```

To install all of them:

```bash
$ pdm install -d
```

For more CLI usage, please refer to [Manage Dependencies](usage/dependency.md)

### Include and exclude package files

The way of specifying include and exclude files are simple, they are given as a list of glob patterns:

```toml
includes = [
    "**/*.json",
    "mypackage/",
]
excludes = [
    "mypackage/_temp/*"
]
```

If neither `includes` or `excludes` is given, PDM is also smart enough to include top level packages and all data files in them.
Packages can also lie in `src` directory that PDM can find it.

### Select another package directory to look for packages

Similar to `setuptools`' `package_dir` setting, one can specify another package directory, such as `src`, in `pyproject.toml` easily:

```toml
package-dir = "src"
```

If no package directory is given, PDM can also recognize `src` as the `package-dir` implicitly if:

1. `src/__init__.py` doesn't exist, meaning it is not a valid Python package, and
2. There exist some packages under `src/*`.

### Implicit namespace packages

As specified in [PEP 420](https://www.python.org/dev/peps/pep-0420), a directory will be recognized as a namespace package if:

1. `<package>/__init__.py` doesn't exist, and
2. There exist normal packages and/or other namespace packages under `<package>/*`, and
3. `<package>` is not specified as `package-dir`

### Build C extensions

Currently, building C extensions still relies on `setuptools`. You should write a python script which contains
a function named `build` and accepts the parameter dictionary of `setup()` as the only argument.
Update the dictionary with your `ext_modules` settings in the function.

Here is an example taken from `MarkupSafe`:

```python
# build.py
from setuptools import Extension

ext_modules = [Extension("markupsafe._speedups", ["src/markupsafe/_speedups.c"])]

def build(setup_kwargs):
    setup_kwargs.update(ext_modules=ext_modules)
```

Now, specify the build script path via `build` in the `pyproject.toml`:

```toml
# pyproject.toml
[tool.pdm]
build = "build.py"
```
