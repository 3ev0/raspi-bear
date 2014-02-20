import setuptools
setuptools.setup(
    name = "RaspiBear",
    version = "0.1",
    packages = ["raspibear"],
    author = "3v0o",
    description = "RaspiBear web interface. A web interface and REST for controlling the RaspiBear!",
    license = "Apache",
    entry_points = {
        'console_scripts': ['raspibear = raspibear.cli:main']
    }
)
