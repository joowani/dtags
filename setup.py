from __future__ import print_function

from setuptools import setup, find_packages
from setuptools.command.install import install

version = {}
with open('./dtags/version.py') as fp:
    exec(fp.read(), version)

with open('./README.rst') as fp:
    description = fp.read()


post_install_msg = """
Finished installing dtags {version}.
To activate dtags, place the following line in your shell config:

  For zsh, place in ~/.zshrc:
  command -v dtags-activate > /dev/null 2>&1 && eval "`dtags-activate zsh`"

  For bash, place in ~/.bashrc (or ~/.bash_profile for OS X):
  command -v dtags-activate > /dev/null 2>&1 && eval "`dtags-activate bash`"

  For fish, place in ~/.config/fish/config.fish:
  command -v dtags-activate > /dev/null 2>&1; and dtags-activate fish | source

And then restart your shell.""".format(version=version['VERSION'])


class DTagsInstall(install):
    def run(self):
        install.run(self)
        self.execute(lambda: None, [], msg=post_install_msg)

setup(
    name='dtags',
    version=version['VERSION'],
    description='Directory Tags for Lazy Programmers',
    long_description=description,
    author='Joohwan Oh',
    author_email='joohwan.oh@outlook.com',
    url='https://github.com/joowani/dtags',
    packages=find_packages(),
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Natural Language :: English',
        'Topic :: Utilities',
    ],
    cmdclass={'install': DTagsInstall},
    entry_points={
        'console_scripts': [
            'e = dtags.commands.e:main',
            'p = dtags.commands.p:main',
            'dtags-t = dtags.commands.t:main',
            'dtags-u = dtags.commands.u:main',
            'dtags-manage = dtags.commands:manage',
            'dtags-refresh = dtags.commands:refresh',
            'dtags-activate = dtags.commands:activate',
        ],
    }
)
