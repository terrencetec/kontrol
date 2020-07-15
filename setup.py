import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="kontrol", # Replace with your own username
    version="0.0.1",
    author="TSANG Terrence Tak Lun",
    author_email="ttltsang@link.cuhk.edu.hk",
    description="KAGRA control python package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/terrencetec/kontrol",
    packages=setuptools.find_packages(),
    # packages=[
    #
    # ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'numpy',
        'scipy',
        'matplotlib',
        'control'
    ]
)
