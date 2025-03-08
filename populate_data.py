import os
from app import create_app, db
from app.models import ClothingItem

app = create_app()

# Dummy data
dummy_data = [
    {
        "name": "Red T-Shirt",
        "category": "Tops",
        "main_color": "Red",
        "secondary_color": "White",
        "image_url": "https://example.com/red_tshirt.jpg",
        "location": "London",
    },
    {
        "name": "Blue Jeans",
        "category": "Bottoms",
        "main_color": "Blue",
        "secondary_color": "Black",
        "image_url": "https://example.com/blue_jeans.jpg",
        "location": "Stockholm",
    },
    {
        "name": "Green Jacket",
        "category": "Outerwear",
        "main_color": "Green",
        "secondary_color": "Gray",
        "image_url": "https://example.com/green_jacket.jpg",
        "location": "London",
    },
    {
        "name": "Black Sneakers",
        "category": "Footwear",
        "main_color": "Black",
        "secondary_color": "White",
        "image_url": "https://example.com/black_sneakers.jpg",
        "location": "Stockholm",
    },
]

with app.app_context():
    for item in dummy_data:
        clothing_item = ClothingItem(
            name=item["name"],
            category=item["category"],
            main_color=item["main_color"],
            secondary_color=item["secondary_color"],
            image_url=item["image_url"],
            location=item["location"],
        )
        db.session.add(clothing_item)
    db.session.commit()

print("Dummy data populated successfully!")
