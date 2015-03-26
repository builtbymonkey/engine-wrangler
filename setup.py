from os import path
from setuptools import setup

setup(
    name = 'engine-wrangler',
    version = '0.2',
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
        'MySQL-python'
    ]
)
