import os
import sys
import subprocess
from setuptools import setup, find_packages, Extension

if sys.version_info[:2] == (3, 6):
    clinic_file = "tools/py36_clinic.py"
else:
    raise ValueError("Must run on Python 3.6")

repo_root = os.path.dirname(os.path.abspath(__file__))

tool_env = os.environ.copy()
tool_env["PYTHONPATH"] = os.path.join(repo_root, "tools") \
    + ":" + tool_env.get("PYTHONPATH", "")
subprocess.run([sys.executable, clinic_file, f"src/asyncio/_asynciomodule.c"],
                env=tool_env)

asyncio_mod = Extension(
    "asyncio._asyncio",
    libraries=["rt"] if sys.platform == 'linux' else [],
    sources=["src/asyncio/_asynciomodule.c"],
)

def execfile(fname, globs, locs=None):
    locs = locs or globs
    exec(compile(open(fname).read(), fname, "exec"), globs, locs)

version_file_path = os.path.join(repo_root, "src", "asyncio", "_version.py")
version_ns = {"__file__": version_file_path}
execfile(version_file_path, version_ns)
version = version_ns["__version__"]

setup(
    name="asyncio37",
    version=version,
    author="Wenjun Si",
    author_email="swj0066@gmail.com",
    description="Backport of asyncio in Python 3.7",
    long_description=open(os.path.join(repo_root, "README.rst"),
                          encoding="utf-8").read(),
    long_description_content_type="text/x-rst",
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries",
    ],
    url="https://github.com/mars-project/asyncio37",
    packages=["", "asyncio"],
    package_dir={"": "src"},
    package_data={"": ["*.pth"]},
    ext_modules=[asyncio_mod],
)
