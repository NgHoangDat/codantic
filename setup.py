from pathlib import Path
from typing import *

import setuptools

__PACKAGE__ = "codantic"
__VERSION__ = "0.0.3"
__DESCRIPTION__ = "CocoDataset reader"
__AUTHOR__ = "nghoangdat"
__EMAIL__ = "18.hoang.dat.12@gmail.com"

CURRENT_DIR = Path(__file__).resolve().parent
with open(CURRENT_DIR / "README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def read_requirements(path: Union[str, Path]):
    with open(path, "r") as fh:
        return {line.strip() for line in fh.readlines() if not line.startswith("#")}


requirements = list(read_requirements(CURRENT_DIR / "requirements.txt"))
extras_require = {"all": set()}

packages = setuptools.find_packages()
sub_packages = []
for sub_requirement in (CURRENT_DIR / __PACKAGE__ / "modules").rglob(
    "requirements.txt"
):
    sub_package = sub_requirement.parent.relative_to(CURRENT_DIR)
    sub_requirements = read_requirements(sub_requirement)
    extras_require[sub_package.name] = sub_requirements
    extras_require["all"].update(sub_requirements)

extras_require = {key: list(val) for key, val in extras_require.items()}

entry_points = {"console_scripts": (f"{__PACKAGE__} = {__PACKAGE__}.__main__:main",)}


setuptools.setup(
    name=__PACKAGE__,
    packages=packages,
    version=__VERSION__,
    author=__AUTHOR__,
    author_email=__EMAIL__,
    description=__DESCRIPTION__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points=entry_points,
    extras_require=extras_require,
    install_requires=requirements,
    include_package_data=True,
    keywords=[],
)
