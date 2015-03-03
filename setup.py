from os import path
from setuptools import setup

setup(
    name = 'engine-wrangler',
    version = '0.1',
    scripts = [
        path.join('scripts', 'ew')
    ],
    packages = [
        'enginewrangler',
        'enginewrangler.formatters',
        'enginewrangler.vendor'
    ],
    install_requires = [
        'MySQL-python'
    ]
)
