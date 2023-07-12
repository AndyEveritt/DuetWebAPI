from setuptools import find_packages, setup
import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="duetwebapi",
    version="1.4.0-b0",
    include_package_data=True,
    packages=find_packages(),

    install_requires=[
        "requests >= 2.31.0",
    ],

    author="Andy Everitt",
    author_email="andreweveritt@e3d-online.com",
    description="Python interface to Duet REST API",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/AndyEveritt/DuetWebAPI",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
