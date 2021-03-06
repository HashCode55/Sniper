"""
Setup file

author: HashCode55
data  : 09/12/2017
"""

import setuptools
from sniper.version import Version

setuptools.setup(name='pysniper',
                 version=Version('1.0.0').number,
                 description='Sniper is a clould enabled, terminal based easy to use snippet manager.',
                 long_description=open('README.md').read().strip(),
                 author='HashCode55',
                 author_email='mehul.ahuja09@gmail.com',                 
                 py_modules=['sniper'],
                 install_requires=[
                     'Click',
                     'clipboard',
                     'fuzzywuzzy', 
                     'python-Levenshtein'
                 ],
                 entry_points='''
                    [console_scripts]
                    sniper = sniper.main:run
                 ''',
                 license='MIT License',
                 zip_safe=False)






