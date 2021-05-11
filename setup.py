from setuptools import setup, find_packages

setup(
    name="stock-backtest",
    version="0.1.1",
    description="stock-backtest is a python library \
        for stock technical analysis backtest on Python 3.7 and above.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    author="10mohi6",
    author_email="10.mohi.6.y@gmail.com",
    url="https://github.com/10mohi6/stock-backtest-python",
    keywords="stock python backtest technical analysis trading strategy",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "yfinance",
        "matplotlib",
    ],
    python_requires=">=3.7.0",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Operating System :: OS Independent",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
    ],
)
