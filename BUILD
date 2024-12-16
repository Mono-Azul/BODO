# Prepare venv and pip
For Windows please use Python 3.12 (pymssql was not building with 3.13) and prepare system for C++ building and running

# Bundle with pyinstaller
Linux:
pyinstaller --onefile --add-data "static:static" --add-data "templates:templates" -n BODO webengine.py

Windows:
First rename webengine.py to webengine.pyw to get rid of the command window!
pyinstaller --onefile --add-data "static;static" --add-data "templates;templates" -n BODO -w webengine.pyw
