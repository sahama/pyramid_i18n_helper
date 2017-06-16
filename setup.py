import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

requires = [
    'pyramid',
    'pyramid_jinja2',
    'deform',
    'pyramid_layout',
    'polib',
    'paginate',
    'babel',
    'pyramid_flash_message',
    ]


setup(name='pyramid_i18n_helper',
      version='0.2.14',
      description='Small tool to help in i18n and l10n',
      long_description=README,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Software Development :: Internationalization",
          "Topic :: Software Development :: Localization",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='Sayyid Hamid Mahdavi',
      author_email='sayyid.hamid.mahdavi@gmail.com',
      url='https://github.com/sahama/pyramid_i18n_helper',
      keywords='web wsgi bfg pylons pyramid i18n l10n',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      extras_require={},
      install_requires=requires,
      )
