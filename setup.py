from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='opticut',
    version='0.0.1',
    packages=['opticut',],
    description="Solves the one dimensional cutting stock problem.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SinaHKazemi/opticut",
    author="Sina Hajikazemi",
    author_email="sina.hkazemi@gmail.com",
    license="MIT",
    entry_points={
        "console_scripts": [
            "opticut=opticut.__main__:cli",
        ]
    },
    install_requires=[
        'pyomo',
    ],
)