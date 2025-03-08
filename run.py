# backend/run.py
from app import create_app, db
import os

app = create_app()

# with app.app_context():
#     db.create_all()

if __name__ == "__main__":
    if os.getenv("FLASK_ENV") == "dev":
        app.run(debug=True)
    else:
        app.run()
