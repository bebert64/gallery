import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gallery",  # Replace with your own username
    version="0.1",
    author="Don Beberto",
    author_email="bebert64@gmail.com",
    description="A gallery QWidget for managing objects through tags",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    package_data={"gallery": ["py.typed"]},
    packages=setuptools.find_packages(include=["gallery", "gallery.*"]),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License",
        "Operating System :: Windows",
    ],
    python_requires=">=3.8",
)
