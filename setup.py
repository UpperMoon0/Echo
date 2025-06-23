#!/usr/bin/env python3
"""
Setup script for Web Scout MCP Client
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="web-scout-mcp-client",
    version="0.1.0",
    author="Web Scout Team",
    author_email="team@webscout.dev",
    description="A command-line client for the Web Scout MCP Server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/web-scout-mcp-client",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: HTML",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "webscout=client:main",
            "web-scout=client:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)