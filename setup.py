from setuptools import setup, find_packages

setup(
    name="dtags",
    description="Directory tags for the lazy programmers",
    long_description=open('README.md').read(),
    version="1.0.0",
    url="https://github.com/joowani/dtags",
    author="Joohwan Oh",
    author_email="joohwan.oh@outlook.com",
    packages=find_packages(),
    install_requires=["argcomplete"],
    entry_points={
        'console_scripts': [
            'run = dtags.commands.run:main',
            'tag = dtags.commands.tag:main',
            'tags = dtags.commands.tags:main',
            'untag = dtags.commands.untag:main',
        ],
    },
)
