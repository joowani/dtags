from setuptools import setup, find_packages

setup(
    name='dtags',
    version='1.0.9',
    description='Directory tags for lazy programmers',
    author='Joohwan Oh',
    author_email='joohwan.oh@outlook.com',
    url='https://github.com/joowani/dtags',
    download_url='https://github.com/joowani/dtags/tarball/1.0.9',
    packages=find_packages(),
    install_requires=['argcomplete'],
    entry_points={
        'console_scripts': [
            'run = dtags.commands.run:main',
            'tag = dtags.commands.tag:main',
            'tags = dtags.commands.tags:main',
            'untag = dtags.commands.untag:main',
        ],
    },
)
