# Open POS API
 
Point-of-sale REST API built with Flask, PostgreSQL and Flask-Admin.
 
## Documentation
 
All docs are in the [docs/](docs/) folder:
 
1. [Requirements](docs/01-requirements.md): what to install (Python 3.8, PostgreSQL, Git, uv)
2. [Setup](docs/02-setup.md): one-time setup steps
3. [Running](docs/03-running.md): start and stop the server
4. [API testing](docs/04-api-testing.md): curl commands, plus a [Postman collection](docs/open-pos-api.postman_collection.json)
5. [Troubleshooting](docs/05-troubleshooting.md): common errors and known bugs
 
## Quick start
 
```powershell
uv venv pos_venv --python 3.8
uv pip install --python pos_venv -r requirements.txt
.\pos_venv\Scripts\activate
python manager.py create_db
python manager.py create_admin -e admin@example.com -p admin123
python manager.py runserver -h 127.0.0.1 -p 5000
```
 
Open http://127.0.0.1:5000/api/v1/login/ and log in with `admin@example.com` / `admin123`.