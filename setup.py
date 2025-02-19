import setuptools

version = {
    "year" :2025,
    "minor" :0,
    "patch" :4
}

setuptools.setup(
    name='cbuild',
    version=f"{version["year"]}.{version["minor"]}.{version["patch"]}",
    description='A command-line build tool for C without the bloat of CMake.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Izaiyah Stokes',
    author_email='d34d0s.dev@gmail.com',
    url='https://github.com/r3shape/cbuild',
    packages=setuptools.find_packages(),
    install_requires=[
        "rich"
    ],
    entry_points={
        'console_scripts': [
            'cbuild = cbuild:main'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)