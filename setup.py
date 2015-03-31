from os import path
from setuptools import setup

setup(
    name = 'engine-wrangler',
    version = '1.1',
    scripts = [
        path.join('scripts', 'ew')
    ],
    packages = [
        'enginewrangler',
        'enginewrangler.formatters',
        'enginewrangler.valuetypes',
        'enginewrangler.vendor'
    ],
    install_requires = [
        'MySQL-python',
        'phpserialize'
    ]
)
