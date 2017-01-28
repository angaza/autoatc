import setuptools
import setuptools.extension


def get_readme_rst():
    with open("README.rst") as readme_file:
        return readme_file.read()

setuptools.setup(
    name="autoatc",
    description="external tool(s) for Augmented Traffic Control (ATC)",
    long_description=get_readme_rst(),
    url="http://github.com/angaza/autoatc",
    author="Angaza",
    license="MIT",
    version="0.1.0",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 2.7",
        "Operating System :: POSIX :: Linux",
        "Topic :: Internet",
        "Topic :: System :: Networking",
        "Topic :: Utilities"],
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        "requests>=2.4.2",
        "netaddr>=0.7.19"],
    entry_points={
        "console_scripts": [
            "autoatc-ensure = autoatc.tools.ensure:main"]})
