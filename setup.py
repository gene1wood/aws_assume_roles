from distutils.core import setup

setup(
    name='aws_assume_roles',
    version='0.1.11',
    author='Gene Wood',
    author_email='gene_wood@cementhorizon.com',
    packages=['aws_assume_roles'],
    entry_points={
          'console_scripts': [
              'aws_assume_roles = aws_assume_roles:main'
          ]
      },
    url='http://pypi.python.org/pypi/aws_assume_roles/',
    license='LICENSE.txt',
    description='Iterate over a set of AWS IAM roles and call an arbitrary '
                'method with each role',
    long_description=open('README.rst').read(),
    install_requires=['boto3'],
)