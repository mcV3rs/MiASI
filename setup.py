import io
import os
from setuptools import find_packages, setup


def read(*paths, **kwargs):
    """Przeczytaj i zwróć zawartość pliku tekstowego
    >>> read("miasi", "VERSION")
    '0.1.0'
    >>> read("README.md")
    ...
    """

    content = ""
    with io.open(
        os.path.join(os.path.dirname(__file__), *paths),
        encoding=kwargs.get("encoding", "utf8"),
    ) as open_file:
        content = open_file.read().strip()
    return content


def read_requirements(path):
    return [
        line.strip()
        for line in read(path).split("\n")
        if not line.startswith(('"', "#", "-", "git+"))
    ]


setup(
    name="miasi",
    version=read("miasi", "VERSION"),
    description="Aplikacja demonstrująca działanie systemu eksperckiego udzielającego rad dotyczących zdrowego trybu życia",
    url="https://github.com/mcV3rs/MiASI/",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="Jakub Gurgul, Adam Paździerz",
    packages=find_packages(exclude=["tests", ".github"]),
    install_requires=read_requirements("requirements.txt"),
    entry_points={
        "console_scripts": ["miasi = miasi.__main__:main"]
    },
    extras_require={
        "test": read_requirements("requirements-test.txt")
        + read_requirements("requirements-base.txt")
    },
)
