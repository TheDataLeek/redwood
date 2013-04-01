from distutils.core import setup

setup(
    name='Redwoodpy',
    version='1.2',
    author='William Farmer',
    author_email='willzfarmer@gmail.com',
    packages=['redwood.py', '.redwoodrc', 'test_redwood.py'],
    scripts=['dir_creation.sh'],
    url='http://pypi.python.org/pypi/Redwoodpy',
    license='LICENSE',
    description='Identifies files with improper age',
    long_description=open('README').read(),
    install_requires=[],
)
