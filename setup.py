from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='qquery',
      version='0.5.8',
      description='Interface to Quicken For Mac database',
      long_description=readme(),
      url='https://github.com/HarryDolan/qquery',
      author='Harry Dolan',
      author_email='harry.dolan@gmail.com',
      license='Unlicense',
      packages=['qquery'],
      entry_points = {
          'console_scripts': ['qquery=qquery.command_line:main'],
          },
)
