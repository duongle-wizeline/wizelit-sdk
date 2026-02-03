from setuptools import setup

setup(
    name="wizelit-sdk",
    version="0.1.31",
    description="Wizelit Agent Wrapper - Internal utility package",
    packages=["wizelit_sdk"],
    entry_points={
        "console_scripts": [
            "wizelit-sdk=wizelit_sdk.cli:main",
        ]
    },
)
