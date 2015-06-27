from cx_Freeze import setup, Executable

# Fore more information:
# http://cx-freeze.readthedocs.org/en/latest/overview.html
# Usage: python setup.py build

# Dependencies
buildOptions = dict(packages = [
"flask",
"flask_httpauth",
"flask_sqlalchemy",
"jinja2",
"markupsafe",
"werkzeug",
"argparse",
"bs4",
"celery",
"itsdangerous",
"nltk",
"passlib",
"dateutil",
"pytz",
"redis",
"six",
"wsgiref",
"elasticsearch",
"numpy",
"sklearn",
"scipy",
"pandas"
], excludes = [])

# Executables to include
executables = [Executable('ml_classifier.py')]

# Config options
setup(name='sara',
      version = '0.1',
      description = 'Attention requests classifier',
      options = dict(build_exe = buildOptions),
      executables = executables)