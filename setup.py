#!/usr/bin/env python3
"""
Setup script for the Email Analyzer.
"""

from setuptools import setup, find_packages

setup(
    name="email_analyzer",
    version="0.1.0",
    description="A tool for analyzing email content and metadata",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/Email_Analyzer",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "email-analyzer=email_analyzer:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Communications :: Email",
        "Topic :: Security",
    ],
    python_requires=">=3.6",
)
