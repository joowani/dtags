from setuptools import find_packages, setup

with open("README.md") as fp:
    long_description = fp.read()

setup(
    name="dtags",
    description="Directory Tags for Lazy Programmers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Joohwan Oh",
    author_email="joohwan.oh@outlook.com",
    url="https://github.com/joowani/dtags",
    keywords=["cli", "terminal"],
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    python_requires=">=3.6",
    license="MIT",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    install_requires=["python-slugify>=4.0.1"],
    extras_require={
        "dev": [
            "black",
            "flake8>=3.8.4",
            "isort>=5.0.0",
            "mypy>=0.790",
            "pre-commit>=2.9.3",
            "pytest>=6.0.0",
            "pytest-cov>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "dtags-activate = dtags.commands.activate:execute",
            "dtags-d = dtags.commands.d:execute",
            "tag = dtags.commands.tag:execute",
            "untag = dtags.commands.untag:execute",
            "run = dtags.commands.run:execute",
            "tags = dtags.commands.tags:execute",
        ],
    },
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
    ],
)
