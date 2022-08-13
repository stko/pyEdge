# setup process thankfully copied from: https://python-packaging.readthedocs.io/en/latest/minimal.html and https://blog.niteoweb.com/setuptools-run-custom-code-in-setup-py/
from setuptools import setup
from setuptools.command.install import install
import subprocess

makeCmd="date" # just a placeholder


class InstallCommand(install):
    """Custom build command."""

    def run(self):
        make_process = subprocess.Popen(
            makeCmd,  shell=True, stderr=subprocess.STDOUT)
        if make_process.wait() != 0:
            pass  # some error handling here?
        install.run(self)


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    include_package_data=True,
    cmdclass={
        'install': InstallCommand,
    },
    name='pyedge',
    version='0.1',
    description='communication library for the pyEdge rabbitMQ network',
    url='https://github.com/stko/pyedge',
    author='Steffen Koehler',
    author_email='steffen@koehlers.de',
    license='pri',
    packages=['pyedge'],
    zip_safe=False)
