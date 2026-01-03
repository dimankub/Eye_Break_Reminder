"""Setup script for EyeCare Reminder"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="eyecare-reminder",
    version="1.0.0",
    author="EyeCare Team",
    description="Cross-platform eye care reminder application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/Eye_Break_Reminder",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "win11toast==0.36.2",
        "win10toast>=0.9",
        "pystray>=0.19.4",
        "Pillow>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "eyecare=main:main",
        ],
    },
)
