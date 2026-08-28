# Student Express

## Run locally

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000/`. Enter a college ID to create or resume the local demo account, then use **Sell** to post a listing with up to five images.

Uploaded media is stored in `media/` for local development. The included SQLite database is development-only; configure PostgreSQL and a managed object store before deploying.
