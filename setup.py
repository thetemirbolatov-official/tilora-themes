from setuptools import setup, find_packages
import os

def get_version():
    with open('VERSION', 'r') as f:
        return f.read().strip()

setup(
    name='tilora-themes-installer',
    version=get_version(),
    author='thetemirbolatov',
    author_email='',
    description='Installer for TILORA VS Code theme',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/thetemirbolatov-official/tilora-themes',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'PyQt5>=5.15.0',
    ],
    entry_points={
        'console_scripts': [
            'tilora-installer=installer:main',
        ],
    },
    include_package_data=True,
    package_data={
        '': ['datas/*', 'datas/**/*'],
    },
)
