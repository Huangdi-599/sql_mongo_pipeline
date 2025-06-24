from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sql-mongo-pipeline",
    version="0.1.0",
    author="Adebayo Ahmed",
    author_email="adebayoh76@gmail.com",
    description="A tool to translate SQL queries into MongoDB aggregation pipelines.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Huangdi-599/sql_mongo_pipeline",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "sqlglot",
        "pymongo",
    ],
    entry_points={
        "console_scripts": [
            "sql-mongo-pipeline=sql_mongo_pipeline.cli:main",
        ],
    },
) 