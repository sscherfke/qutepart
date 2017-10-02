#!/usr/bin/env python3

import sys
import os
import platform

from setuptools import setup, Extension

import distutils.ccompiler
import distutils.sysconfig

sys.path.insert(0, 'qutepart')
import version


howToInstallMsg = """Qutepart installation fails to find PyQt5
if run as `python3 setup.py install`.
Evidently, setuptools doesn't support installing from wheel.
Therefore, only invoke this as:

Unix:
    python3 -m pip install -e .

Windows:
    python3 setup.py build_ext --include-dir=../pcre-8.37/build --lib-dir=../pcre-8.37/build/Release
    python3 -m pip install -e .
"""

def parse_arg_list(param_start):
    """Exctract values like --libdir=bla/bla/bla
    param_start must be '--libdir='
    """
    values = [arg[len(param_start):]
              for arg in sys.argv
              if arg.startswith(param_start)]

    # remove recognized arguments from the sys.argv
    otherArgs = [arg
                 for arg in sys.argv
                 if not arg.startswith(param_start)]
    sys.argv = otherArgs

    return values


def runningOnPip():
  # __file__ in setup gives something like /tmp/pip-DNpsLw-build/setup.py if ran from pip.
  return 'pip' in __file__


if not runningOnPip() and 'install' in sys.argv:
  print(howToInstallMsg)
  sys.exit(0)


packages = ['qutepart', 'qutepart/syntax', 'qutepart/indenter']

package_data = {'qutepart': ['icons/*.png'],
                'qutepart/syntax': ['data/xml/*.xml', 'data/syntax_db.json']
                }


include_dirs = parse_arg_list('--include-dir=')
if not include_dirs:
    include_dirs = ['/usr/include', '/usr/local/include', '/opt/local/include']

library_dirs = parse_arg_list('--lib-dir=')
if not library_dirs:
    library_dirs = ['/usr/lib', '/usr/local/lib', '/opt/local/lib']

macros = []
if platform.system() == 'Windows':
    macros.append(('HAVE_PCRE_CONFIG_H', None))

extension = Extension('qutepart.syntax.cParser',
                      sources=['qutepart/syntax/cParser.c'],
                      libraries=['pcre'],
                      include_dirs=include_dirs,
                      library_dirs=library_dirs,
                      define_macros=macros)



def _checkDependencies():
    compiler = distutils.ccompiler.new_compiler()
    """check if function without parameters from stdlib can be called
    There should be better way to check, if C compiler is installed
    """
    if not compiler.has_function('rand', includes=['stdlib.h']):
        print("It seems like C compiler is not installed or not operable.")
        return False

    if not compiler.has_function('rand',
                                 includes=['stdlib.h', 'Python.h'],
                                 include_dirs=[distutils.sysconfig.get_python_inc()],
                                 library_dirs=[os.path.join(os.path.dirname(sys.executable), 'libs')]):
        print("Failed to find Python headers.")
        print("Try to install python-dev package")
        print("If not standard directories are used, pass parameters")
        print("\tpython setup.py install --lib-dir=c://github/pcre-8.37/build/Release --include-dir=c://github/pcre-8.37/build")
        print("\tpython setup.py install --lib-dir=/my/local/lib --include-dir=/my/local/include")
        print("--lib-dir= and --include-dir= may be used multiple times")
        return False

    if not compiler.has_function('pcre_version',
                                 includes=['pcre.h'],
                                 libraries=['pcre'],
                                 include_dirs=include_dirs,
                                 library_dirs=library_dirs):
        print("Failed to find pcre library.")
        print("Try to install libpcre{version}-dev package, or go to http://pcre.org")
        print("If not standard directories are used, pass parameters:")
        print("\tpython setup.py install --lib-dir=c://github/pcre-8.37/build/Release --include-dir=c://github/pcre-8.37/build")
        print("\tpython setup.py install --lib-dir=/my/local/lib --include-dir=/my/local/include")
        print("--lib-dir= and --include-dir= may be used multiple times")
        return False

    return True


""" A hack to set compiler version for distutils on Windows.
See https://github.com/hlamer/qutepart/issues/52
"""
cfgPath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'setup.cfg'))
if os.name == 'nt':
    with open(cfgPath, 'w') as cfgFile:
        cfgFile.write("[build_ext]\ncompiler=msvc")
else:
    if os.path.isfile(cfgPath):
        os.remove(cfgPath)


if ('install' in sys.argv or
    'build' in sys.argv or
    'build_ext' in sys.argv):
    if '--force' not in sys.argv and '--help' not in sys.argv:
        if os.name != 'nt':
            if not _checkDependencies():
                sys.exit(-1)


setup(name='qutepart',
    version='%s.%s.%s' % version.VERSION,
    description='Code editor component for PyQt5',
    author='Andrei Kopats',
    author_email='hlamer@tut.by',
    url='https://github.com/hlamer/qutepart',
    packages=packages,
    package_data=package_data,
    ext_modules=[extension],
    install_requires = ['PyQt5']

)
