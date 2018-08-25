from setuptools import setup
from version import __version__ as version


setup(name='AutoHunt',
      version=version,
      description='A webscraping solution to collect data from Real Estate agencies.',
      author='Vincent Maladiere',
      url='https://github.com/Vincent-Maladiere/AutoHunt',
      license='MIT',
      install_requires=['pandas', 'selenium', 'gspread', 'oauth2client'],
      classifiers=['Programming Language :: Python :: 3'],
      )
