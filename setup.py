from setuptools import setup, find_packages


setup(
    name="js9331_update",
    version="0.0.1",
    author="Raiser Ma",
    author_email="mraiser@foxmail.com",
    packages=find_packages(),
    install_requires=[
        'Click',
        'pyserial'
    ],
    entry_points={
        'console_scripts': [
        ],
    },
)
