import os
import subprocess
from distutils.errors import LibError
from distutils.core import setup
from distutils.command.build import build as _build
from setuptools.command.develop import develop as _develop

AFL_UNIX_INSTALL_PATH = os.path.join("bin", "afl-unix")
QEMU_BUILD_SUPPORT_PATCH_FILE = os.path.join("patches", "qemu-build-support.diff")
QEMU_EXIT_DOUBLE_READ_PATCH_FILE = os.path.join("patches", "qemu-exit-double-read.diff")
AFL_UPDATE_INTERVAL_PATCH_FILE = os.path.join("patches", "afl-update-interval.diff")
AFL_UNIX_GEN = os.path.join(os.curdir, "patches", "build.sh")
MULTIARCH_LIBRARY_PATH = os.path.join("bin", "fuzzer-libs")


def _setup():
    # revisiting the afl mirrorer repo
    if not os.path.exists(AFL_UNIX_INSTALL_PATH):
        AFL_UNIX_REPO = "https://github.com/AFLplusplus/AFLplusplus.git"
        if subprocess.call(['git', 'clone', AFL_UNIX_REPO, AFL_UNIX_INSTALL_PATH]) != 0:
            raise LibError("Unable to retrieve afl-unix")

        with open(QEMU_BUILD_SUPPORT_PATCH_FILE, "rb") as f:
            if subprocess.check_call(['git', 'apply'],stdin=f, cwd=AFL_UNIX_INSTALL_PATH) != 0:
                raise LibError("Unable to apply qemu build multiarch patch")

        with open(QEMU_EXIT_DOUBLE_READ_PATCH_FILE, "rb") as f:
            if subprocess.check_call(['git', 'apply'],stdin=f, cwd=AFL_UNIX_INSTALL_PATH) != 0:
                raise LibError("Unable to apply qemu exit double read patch")

        with open(AFL_UPDATE_INTERVAL_PATCH_FILE, "rb") as f:
            if subprocess.check_call(['git', 'apply'],stdin=f, cwd=AFL_UNIX_INSTALL_PATH) != 0:
                raise LibError("Unable to apply afl update interval patch")

        if subprocess.call(['cp',AFL_UNIX_GEN, AFL_UNIX_INSTALL_PATH]) != 0:
            raise LibError("Build file doesn't exist")

        if subprocess.check_call(['./build.sh'], cwd=AFL_UNIX_INSTALL_PATH) != 0:
            raise LibError("Unable to build afl-other-arch")

def _setup_libs():
    if not os.path.exists(MULTIARCH_LIBRARY_PATH):
        if subprocess.call(["./fetchlibs.sh"], cwd=".") != 0:
            raise LibError("Unable to fetch libraries")

data_files = [ ]
def _datafiles():
    # for each lib export it into data_files
    for path,_,files in os.walk("bin/fuzzer-libs"):
        libs = [ os.path.join(path, f) for f in files if '.so' in f ]
        if libs:
            data_files.append((path, libs))

    # grab all the executables from afl
    for path,_,files in os.walk(os.path.join("bin", 'afl-unix')):
        if 'qemu-3.' in path:
            continue
        paths = [ os.path.join(path, f) for f in files ]
        exes = [ f for f in paths if os.path.isfile(f) and os.access(f, os.X_OK) ]
        if exes:
            data_files.append((path, exes))

    return data_files

def get_patches():
    # get all patches
    for path,_,files in os.walk("patches"):
        patches = [os.path.join(path, f) for f in files]
        if patches:
            data_files.append((path, patches))

    return data_files

class build(_build):
    def run(self):
        self.execute(_setup, (), msg="Setting up AFL-other-arch")
        self.execute(_setup_libs, (), msg="Getting libraries")
        _datafiles()
        _build.run(self)

class develop(_develop):
    def run(self):
        self.execute(_setup, (), msg="Setting up AFL-other-arch")
        self.execute(_setup_libs, (), msg="Getting libraries")
        _datafiles()
        _develop.run(self)

get_patches()

setup(
    name='shellphish-afl', version='2.0.0', description="pip package for afl++",
    packages=['shellphish_afl'],
    cmdclass={'build': build, 'develop': develop},
    data_files=data_files,
    scripts=['fetchlibs.sh'],
)
