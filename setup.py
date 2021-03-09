from setuptools import setup, find_packages
import pathlib, inspect
import tl

long_description = pathlib.Path("README.md").read_text(encoding="utf-8")
description = inspect.cleandoc(tl.__doc__).splitlines()[0]

setup(name="pytl",
      version=tl.version,
      description=description,
      long_description=long_description,
      url="https://github.com/fpom/pytl",
      author="Franck Pommereau",
      author_email="franck.pommereau@univ-evry.fr",
      classifiers=["Development Status :: 4 - Beta",
                   "Intended Audience :: Developers",
                   "Topic :: Scientific/Engineering",
                   "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
                   "Programming Language :: Python :: 3",
                   "Operating System :: OS Independent"],
      packages=find_packages(where="."),
      python_requires=">=3.7",
      install_requires=["TatSu"],
)
