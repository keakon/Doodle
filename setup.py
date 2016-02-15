from setuptools import setup

from scripts.install import install


setup(
    name="doodle",
    version="2.0.dev1",
    license='MIT',
    description="Doodle",
    packages=['doodle'],
    install_requires=[
        'tornado>=4.3',
        'redis',
        'hiredis',
        'pycurl',
        'ujson',
        'tenjin',
    ],
    entry_points={
        'console_scripts': [
            'doodle = doodle.main:main',
        ],
    },
)

install()
