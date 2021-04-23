#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2021, Dor Yeheskel. All rights reserved.

"""
API for compiling C/C++ code to python module during runtime (via SWIG).

"""

import sys
import tempfile
import os
import subprocess
import platform
from shutil import which, rmtree


def is_tool(name: str):
    """
    Check whether `name` is on PATH and marked as executable.

    @param name: name of the executable (e.g, ls, grep, ...)
    @return: True if it can be execute
    """
    return which(name) is not None


def check_requests():
    # Check OS:
    if platform.system() != 'Linux':
        raise Exception('-E- swig2py - Support only for Linux platforms')

    # Check swig:
    if not (is_tool('swig')):
        raise Exception('-E- swig2py - Swig does not exist. (sudo apt install swig)')

    # Check g++:
    if not (is_tool('g++')):
        raise Exception('-E- swig2py - g++ compiler does not exist. (sudo apt install g++)')

    # Check python-config:
    if not (is_tool('python-config') or is_tool('python3-config')):
        raise Exception('-E- swig2py - g++ compiler does not exist. (sudo apt install python3-dev)')


def execute(command, debug):
    """
    Wrapper to subprocess.Popen.
    In case of an error, it will raise an exception with the info from stderr.

    @param command: command to run in shell
    @param debug: if True, will print the commands and their stdout/stderr
    @return: Tuple of strings: (stdout, stderr)
    """
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    stdout, stderr = stdout.decode('utf-8'), stderr.decode('utf-8')
    if debug:
        print('Command :', ' '.join(command))
        print('Stdout  :', stdout)
        print('Stderr  :', stderr)
        print('-----------------------------------------------')
    if stderr != '':
        raise Exception('Command : ' + command[0] + '\nError   : \\\n' + stderr + '')
    return stdout, stderr


def write_h(code: str, pkg_name: str):
    """
    Write the code to .h file.

    @param code: Code as string.
    @param pkg_name: a dummy name for the new pkg.
    """
    with open(pkg_name + '.h', mode='w') as f:
        f.write(code)
        f.write('\n')


def write_i(pkg_name: str):
    """
    Write the interface file for swig.

    @param pkg_name: a dummy name for the new pkg.
    """
    interface_file = \
        """
    %module {}
    %{{
    #include "{}.h"
    %}}

    %include "{}.h"

    """
    with open(pkg_name + '.i', mode='w') as f:
        f.write(interface_file.format(pkg_name, pkg_name, pkg_name))


def swig(pkg_name: str, debug: bool):
    """
    Generate ".so" file and ".py" file, which can be imported.
    Steps:
        1. swig -c++ -python {}.i
        2. g++ -fPIC -c {}.h
        3. g++ -fPIC -c {}_wrap.cxx `python3-config --cflags`
        4. g++ -shared {}_wrap.o `python3-config --ldflags` -o _{}.so

    @param pkg_name: a dummy name for the new pkg.
    @param debug: if True, will print the commands and their stdout/stderr
    """
    # Swig:
    command = 'swig -c++ -python ./{}.i'.format(pkg_name).split()
    execute(command, debug)

    # Compile code:
    command = 'g++ -fPIC -c {}.h'.format(pkg_name).split()
    execute(command, debug)

    # Get python libs paths:
    py_config = 'python3-config' if is_tool('python3-config') else 'python-config'
    command = (py_config + ' --cflags').split()
    py_libs, _ = execute(command, debug)

    # Compile cxx:
    command = ('g++ -fPIC -c {}_wrap.cxx ' + py_libs).format(pkg_name).split()
    execute(command, debug)

    # Get python LD flags:
    command = (py_config + ' --ldflags').split()
    py_flags, _ = execute(command, debug)

    # Compile wrap:
    command = ('g++ -shared {}_wrap.o ' + py_flags + ' -o _{}.so').format(pkg_name, pkg_name).split()
    execute(command, debug)

    sys.path.insert(0, os.path.realpath("./"))


def import_pkg(code: str, debug=False):
    """
    Input  : C/C++ code.
    Output : Module object.

    @param code: Code as string.
    @param debug: if True, will print the commands and their stdout/stderr
    @return: module object
    """
    check_requests()  # Exception could be raise from here

    # Create tmp dir and change dir:
    cwd_path = os.getcwd()
    tmp_dir = tempfile.TemporaryDirectory().name
    os.mkdir(tmp_dir)
    os.chdir(tmp_dir)

    # Create new pkg:
    pkg_name = 'pkg' + '_' + next(tempfile._get_candidate_names())
    write_h(code, pkg_name)
    write_i(pkg_name)
    swig(pkg_name, debug)

    # Dynamiclly import it and load it to the RAM:
    pkg = __import__(name=pkg_name)

    # Cd to original dir:
    os.chdir(cwd_path)

    # Remove all files:
    # It is safe because the module binary code is already in the RAM, as you can see also in /proc/pid/maps
    rmtree(os.path.realpath(tmp_dir), ignore_errors=True)

    return pkg
