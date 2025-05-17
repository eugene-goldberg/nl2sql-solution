"""
Setup script for the NL2SQL solution package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nl2sql_solution",
    version="0.1.0",
    author="YourName",
    author_email="your.email@example.com",
    description="Natural language to SQL solution using LangChain and Semantic Kernel",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/NL2SQL-Solution-1",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=[
        "semantic-kernel>=0.9.0b1",
        "langchain>=0.1.0",
        "langchain-openai>=0.0.3",
        "langchain-community>=0.0.6",
        "langchain-experimental>=0.0.26",
        "python-dotenv>=1.0.0",
        "sqlalchemy>=2.0.0",
        "pyodbc>=4.0.39",
    ],
)