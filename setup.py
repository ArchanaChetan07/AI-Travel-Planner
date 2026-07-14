from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = [
        line.strip()
        for line in f
        if line.strip() and not line.startswith("#")
    ]

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="ai-travel-planner",
    version="2.0.0",
    author="Sudhanshu",
    description="Tool-loop travel planning agent (weather, attractions, budget) with optional Groq",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ArchanaChetan07/AI-Travel-Planner",
    packages=find_packages(exclude=["tests*", "*.pycache__*"]),
    python_requires=">=3.10",
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
