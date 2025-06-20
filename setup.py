from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='gittty',
    version='0.8.0',
    py_modules=['gittty'],
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'gittty = gittty:main',
        ],
    },
    author='ArtuxF',
    author_email='aflores98@ucol.mx',
    description='A lifeline to clone your essential Git repositories directly from the TTY.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ArtuxF/gittty',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Environment :: Console',
        'Topic :: Software Development :: Version Control :: Git',
    ],
    python_requires='>=3.6',
)
