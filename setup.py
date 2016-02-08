from setuptools import setup, find_packages


setup(
    name='dtags',
    version='1.1.0',
    description='Directory Tags for Lazy Programmers',
    author='Joohwan Oh',
    author_email='joohwan.oh@outlook.com',
    url='https://github.com/joowani/dtags',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'run = dtags.commands.run:main',
            'tag = dtags.commands.tag:main',
            'tags = dtags.commands.tags:main',
            'untag = dtags.commands.untag:main',
            'dtags-rc = dtags.commands.shell:main'
        ],
    }
)
