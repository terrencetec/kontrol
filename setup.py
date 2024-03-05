import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="kontrol", # Replace with your own username
    version="1.0.0-beta.1",
    author="TSANG Terrence Tak Lun",
    author_email="terrencetec@gmail.com",
    description="KAGRA control python package",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/terrencetec/kontrol",
    packages=setuptools.find_packages(include=["kontrol", "kontrol.*"]),
    # packages=[
    #     "kontrol",
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
        'control>=0.9'
    ],
    extra_requires={
        "ezca":["ezca"]
    },
)
