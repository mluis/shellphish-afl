import os
import distutils

if not hasattr(distutils, 'sysconfig'):
    import distutils.sysconfig

def afl_bin(platform):
    return os.path.join(afl_dir(platform), 'afl-fuzz')

def afl_path_var(platform):
    return os.path.join(afl_dir(platform), 'tracers', platform)

def afl_dir(platform):
    return os.path.join(_all_base(), 'afl-unix')

def _all_base():
    if __file__.startswith(distutils.sysconfig.PREFIX):
        return os.path.join(distutils.sysconfig.PREFIX, 'bin')
    else:
        return os.path.join(os.path.dirname(__file__), '..', 'bin')
