#!/usr/bin/env python3
"""
Setup script for OpenShift MCP Server
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="openshift-mcp-server",
    version="1.0.0",
    author="OpenShift MCP Server Developer",
    description="A Model Context Protocol (MCP) server for OpenShift cluster management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/openshift-mcp-server",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "openshift-mcp-server=openshift_mcp_server:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 