from setuptools import setup, find_packages

setup(
    name="prism",
    version="0.1.0",
    description="Vendor-Agnostic Network Device Compliance Engine",
    author="PRISM Team (SIH)",
    author_email="team@prism.local",
    url="https://github.com/SwarnavChatterjee/PRISM",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.104.0",
        "python-multipart>=0.0.20",
        "pydantic>=2.5.0",
        "pyyaml>=6.0.0",
        "uvicorn>=0.24.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "Topic :: System :: Networking",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
    ],
)
