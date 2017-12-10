import setuptools
from sniper.version import Version


setuptools.setup(name='Sniper',
                 version=Version('1.0.0').number,
                 description='Snipe the Snippet',
                 long_description=open('README.md').read().strip(),
                 author='HashCode55',
                 author_email='mehul.ahuja09@gmail.com',
                 url='http://path-to-my-packagename',
                 py_modules=['sniper'],
                 install_requires=[
                     'Click'
                 ],
                 entry_points='''
                    [console_scripts]
                    sniper = sniper.main:run
                 ''',
                 license='MIT License',
                 zip_safe=False,                 
                 classifiers=['Packages', 'Boilerplate'])
