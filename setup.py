import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ssm-menu-pkg-paul-seward", # Replace with your own username
    version="1.0.3",
    author="Paul Seward",
    author_email="paul.seward@ascential.com",
    description="An AWS SSM Menu",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/paulsewardasc/ssm-menu",
    license="MIT",
    #packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["ssm-menu"],
    #install_requires=["boto3","json","time","os","sys","pathlib","simple_term_menu","collections"],
    install_requires=["boto3","simple_term_menu","collections"],
    include_package_data=True,
    entry_points={
      "console_scripts": [
        "ssmmenu=ssmmenu.py:main",
        "ssm=ssm.py:main",
      ]
    },
)
