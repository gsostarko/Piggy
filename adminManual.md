## Stvaranje virtualnog okruženja

'''python
python -m venv piggy
'''

## Aktivacija virtualnog okruženja

'''python
piggy/Scripts/activate
'''

## deaktivacija virtualnog okruženja

'''python
deactivate
'''

## provjera paket koji su instalirani

'''python
pip freeze
'''

## instalacija Flaska

'''python
pip install flask
'''

set FLASK_ENV=development
set FLASK_APP=main.py
set FLASK_DEBUG=1
flask --app main --debug run
