import setuptools
setuptools.setup(
    name="Yevolve",
    version="0.0.1",
    author="Keith Gallimore",
    author_email="kga11imore@yahoo.com",
    description="Auto host random videos on youtube stream",
    url="https://github.com/trenchguns/yevolve",
    packages=['pytube3', 'requests', 'beautifulsoup4', 'urllib3'],
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
    python_requires='>=3.6',
)
