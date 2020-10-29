from setuptools import find_packages, setup

setup(
    name="duetwebapi",
    version="0.0.1",
    include_package_data=True,
    packages=find_packages(),

    install_requires=[
        "requests >= 2.22.0",
    ],

    author="Andy Everitt",
    author_email="andreweveritt@e3d-online.com",
    description="Python interface to Duet REST API",
    url="https://github.com/AndyEveritt/DuetWebAPI",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
