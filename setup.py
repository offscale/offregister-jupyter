# -*- coding: utf-8 -*-

"""
setup.py implementation, interesting because it parsed the first __init__.py and
    extracts the `__author__` and `__version__`
"""

import sys
from ast import Assign, Name, parse
from functools import partial
from operator import attrgetter
from os import listdir, path
from os.path import extsep

from setuptools import find_packages, setup

if sys.version_info[:2] >= (3, 12):
    import os
    from sysconfig import _BASE_EXEC_PREFIX as BASE_EXEC_PREFIX
    from sysconfig import _BASE_PREFIX as BASE_PREFIX
    from sysconfig import _EXEC_PREFIX as EXEC_PREFIX
    from sysconfig import _PREFIX as PREFIX
    from sysconfig import get_python_version

    def is_virtual_environment():
        """
        Whether one is in a virtual environment
        """
        return sys.base_prefix != sys.prefix or hasattr(sys, "real_prefix")

    def get_python_lib(plat_specific=0, standard_lib=0, prefix=None):
        """Return the directory containing the Python library (standard or
        site additions).

        If 'plat_specific' is true, return the directory containing
        platform-specific modules, i.e. any module from a non-pure-Python
        module distribution; otherwise, return the platform-shared library
        directory.  If 'standard_lib' is true, return the directory
        containing standard Python library modules; otherwise, return the
        directory for site-specific modules.

        If 'prefix' is supplied, use it instead of sys.base_prefix or
        sys.base_exec_prefix -- i.e., ignore 'plat_specific'.
        """
        is_default_prefix = not prefix or os.path.normpath(prefix) in (
            "/usr",
            "/usr/local",
        )
        if prefix is None:
            if standard_lib:
                prefix = plat_specific and BASE_EXEC_PREFIX or BASE_PREFIX
            else:
                prefix = plat_specific and EXEC_PREFIX or PREFIX

        if os.name == "posix":
            if plat_specific or standard_lib:
                # Platform-specific modules (any module from a non-pure-Python
                # module distribution) or standard Python library modules.
                libdir = sys.platlibdir
            else:
                # Pure Python
                libdir = "lib"
            libpython = os.path.join(prefix, libdir, "python" + get_python_version())
            if standard_lib:
                return libpython
            elif is_default_prefix and not is_virtual_environment():
                return os.path.join(prefix, "lib", "python3", "dist-packages")
            else:
                return os.path.join(libpython, "site-packages")
        elif os.name == "nt":
            if standard_lib:
                return os.path.join(prefix, "Lib")
            else:
                return os.path.join(prefix, "Lib", "site-packages")
        else:

            class DistutilsPlatformError(Exception):
                """DistutilsPlatformError"""

            raise DistutilsPlatformError(
                "I don't know where Python installs its library "
                "on platform '%s'" % os.name
            )

    from ast import Del as Str
else:
    from ast import Str
    from distutils.sysconfig import get_python_lib

if sys.version_info[0] == 2:
    from itertools import ifilter as filter
    from itertools import imap as map

if sys.version_info[:2] > (3, 7):
    from ast import Constant
else:
    from ast import expr

    # Constant. Will never be used in Python =< 3.8
    Constant = type("Constant", (expr,), {})


package_name_verbatim = "offregister-jupyter"
package_name = package_name_verbatim.replace("-", "_")

with open(
    path.join(path.dirname(__file__), "README{extsep}md".format(extsep=extsep)), "rt"
) as fh:
    long_description = fh.read()


def to_funcs(*paths):
    """
    Produce function tuples that produce the local and install dir, respectively.

    :param paths: one or more str, referring to relative folder names
    :type paths: ```*paths```

    :return: 2 functions
    :rtype: ```Tuple[Callable[Optional[List[str]], str], Callable[Optional[List[str]], str]]```
    """
    return (
        partial(path.join, path.dirname(__file__), package_name, *paths),
        partial(path.join, get_python_lib(prefix=""), package_name, *paths),
    )


def main():
    """Main function for setup.py; this actually does the installation"""
    with open(
        path.join(
            path.abspath(path.dirname(__file__)),
            package_name,
            "__init__{extsep}py".format(extsep=extsep),
        )
    ) as f:
        parsed_init = parse(f.read())

    __author__, __version__, __description__ = map(
        lambda node: node.value if isinstance(node, Constant) else node.s,
        filter(
            lambda node: isinstance(node, (Constant, Str)),
            map(
                attrgetter("value"),
                filter(
                    lambda node: isinstance(node, Assign)
                    and any(
                        filter(
                            lambda name: isinstance(name, Name)
                            and name.id
                            in frozenset(
                                ("__author__", "__version__", "__description__")
                            ),
                            node.targets,
                        )
                    ),
                    parsed_init.body,
                ),
            ),
        ),
    )
    _data_join, _data_install_dir = to_funcs("_data")
    _conf_join, _conf_install_dir = to_funcs("configs")

    setup(
        name=package_name_verbatim,
        author=__author__,
        author_email="807580+SamuelMarks@users.noreply.github.com",
        version=__version__,
        url="https://github.com/offscale/{}".format(package_name_verbatim),
        description=__description__,
        long_description=long_description,
        long_description_content_type="text/markdown",
        classifiers=[
            "Development Status :: 7 - Inactive",
            "Intended Audience :: Developers",
            "Topic :: Software Development",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
            "License :: OSI Approved :: Apache Software License",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
        ],
        license="(Apache-2.0 OR MIT OR CC0-1.0)",
        license_files=["LICENSE-APACHE", "LICENSE-MIT", "LICENSE-CC0"],
        install_requires=[
            "paramiko",
            "pyyaml",
            "invoke >= 2.0 ; python_version>='3.5'",
            "fabric >= 2.7.1 ; python_version>='3.5'",
            "fabric == 2.7.1 ; python_version<'3.5'",
        ],
        test_suite="{}{}tests".format(package_name, path.extsep),
        packages=find_packages(),
        package_dir={package_name: package_name},
        data_files=[
            (_data_install_dir(), list(map(_data_join, listdir(_data_join())))),
            (_conf_install_dir(), list(map(_conf_join, listdir(_conf_join())))),
        ],
    )


def setup_py_main():
    """Calls main if `__name__ == '__main__'`"""
    if __name__ == "__main__":
        main()


setup_py_main()
