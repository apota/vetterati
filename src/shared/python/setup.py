from setuptools import setup, find_packages

setup(
    name="vetterati-shared",
    version="1.0.0",
    description="Shared utilities and models for Vetterati ATS services",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "pydantic>=2.5.0",
        "sqlalchemy>=2.0.23",
        "asyncpg>=0.29.0",
        "redis>=5.0.1",
        "httpx>=0.25.2",
        "python-dateutil>=2.8.2",
        "typing-extensions>=4.8.0",
    ],
)
