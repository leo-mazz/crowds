import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

VERSION = '0.0.1'
PACKAGE_NAME = 'crowds'
AUTHOR = 'Leonardo Mazzone'
AUTHOR_EMAIL = 'leo@mazzone.space'
URL = 'https://github.com/leo-mazz/crowds'

LICENSE = 'GNU Affero General Public License v3.0'
DESCRIPTION = 'A collection of anonymization algorithms in Python '
LONG_DESCRIPTION = (HERE / "README.md").read_text()
LONG_DESC_TYPE = "text/markdown"

INSTALL_REQUIRES = [
      'pandas >= 0.25.1'
]

setup(name=PACKAGE_NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      long_description_content_type=LONG_DESC_TYPE,
      author=AUTHOR,
      license=LICENSE,
      author_email=AUTHOR_EMAIL,
      url=URL,
      install_requires=INSTALL_REQUIRES,
      packages=find_packages()
      )