# backend/app/models.py
from . import db
from datetime import datetime, timezone


class ClothingItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    main_color = db.Column(db.String(30), nullable=False)
    secondary_color = db.Column(db.String(30), nullable=True)
    image_url = db.Column(db.String(255), nullable=True)  # Changed to nullable=True to make it optional
    location = db.Column(db.String(50), nullable=False)
    count = db.Column(db.Integer, default=1)
    created_on = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def __repr__(self):
        return f"<ClothingItem {self.name}>"
