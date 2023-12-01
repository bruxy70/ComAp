import setuptools

REVISION = '0.3.0'
PROJECT_NAME = 'comap'
PROJECT_AUTHORS = "Václav Chaloupka"
PROJECT_EMAILS = 'vasek.chaloupka@hotmail.com'
PROJECT_URL = "https://github.com/bruxy70/ComAp"
SHORT_DESCRIPTION = 'Allows easy automation of WebSupervisor tasks, such as downloading and analyzing data'

with open("README.md", "r") as fh:
    LONG = fh.read()

setuptools.setup(
    name=PROJECT_NAME.lower(),
    python_requires=">=3.11.0",
    version=REVISION,
    author=PROJECT_AUTHORS,
    author_email=PROJECT_EMAILS,
    packages=setuptools.find_packages(exclude=('config.py',)),
    install_requires=[
        'asyncio',
        'aiohttp',
        'async_timeout',
        'requests',
        'aiofiles',
        'timestring',
    ],
    url=PROJECT_URL,
    description=SHORT_DESCRIPTION,
    long_description=LONG,
    long_description_content_type="text/markdown",
    license='MIT',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
    ],
)
