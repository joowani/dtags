from setuptools import setup, find_packages

version = {}
with open('./dtags/version.py') as fp:
    exec(fp.read(), version)

setup(
    name='dtags',
    version=version['VERSION'],
    description='Directory Tags for Lazy Programmers',
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
    entry_points={
        'console_scripts': [
            'e = dtags.commands.execute:main',
            'tag = dtags.commands.tag:main',
            'untag = dtags.commands.untag:main',
            'dtags = dtags.commands.manage:main',
        ],
    }
)
