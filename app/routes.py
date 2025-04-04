import os
import boto3
from flask import Blueprint, jsonify, request
from PIL import Image, ImageOps
from io import BytesIO
from .models import ClothingItem
from . import db
import logging

logging.basicConfig()

main = Blueprint("main", __name__)

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_S3_REGION"),
)


@main.route("/")
def home():
    return jsonify({"message": "Welcome to the Digital Wardrobe API!"})


def upload_image_to_s3_and_get_url(image_file, item_name):
    # Resize the image and fix orientation
    image = Image.open(image_file)
    image = image.convert("RGB")
    image = ImageOps.exif_transpose(image)

    image.thumbnail((800, 800))  # Resize image to a maximum of 800x800 pixels

    # Save the image to a BytesIO object
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format="JPEG")  # Save as JPEG
    img_byte_arr.seek(0)  # Move to the beginning of the BytesIO object

    # Create a unique image name
    image_name = f"{item_name.replace(' ', '_')}.jpg"

    # Upload the image to S3
    s3_client.upload_fileobj(
        img_byte_arr,
        os.getenv("AWS_S3_BUCKET_NAME"),
        image_name,
        ExtraArgs={"ContentType": "image/jpeg"},
    )

    return f"https://{os.getenv('AWS_S3_BUCKET_NAME')}.s3.amazonaws.com/{image_name}"


# Create a new clothing item
@main.route("/clothing", methods=["POST"])
def create_clothing_item():
    data = request.form  # Use request.form to get form data
    
    # Validate location
    if data["location"] not in ["London", "Stockholm"]:
        return jsonify({"error": "Location must be either London or Stockholm."}), 400

    count = int(data.get("count", 1))
    
    # Make image upload optional
    s3_image_url = None
    if "image_url" in request.files:
        image_file = request.files["image_url"]
        if image_file.filename:  # Only upload if a file was actually selected
            s3_image_url = upload_image_to_s3_and_get_url(image_file, data["name"])

    logging.info("creating clothing item")
    # Create a new clothing item
    new_item = ClothingItem(
        name=data["name"],
        category=data["category"],
        main_color=data["main_color"],
        secondary_color=data.get("secondary_color"),
        image_url=s3_image_url,  # This can now be None
        location=data["location"],
        count=count,  # Set the count
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify({"message": "Clothing item created!"}), 201


# Get all clothing items
@main.route("/clothing", methods=["GET"])
def get_clothing_items():
    items = ClothingItem.query.all()
    result = []
    for item in items:
        result.append(
            {
                "id": item.id,
                "name": item.name,
                "category": item.category,
                "main_color": item.main_color,
                "secondary_color": item.secondary_color,
                "image_url": item.image_url,
                "location": item.location,
                "count": item.count,
                "created_on": item.created_on.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),  # Format the date
            }
        )
    return jsonify(result)


# Update a clothing item
@main.route("/clothing/<int:item_id>", methods=["PUT"])
def update_clothing_item(item_id):
    item = ClothingItem.query.get_or_404(item_id)

    # Get the form data
    data = request.form
    item.name = data["name"]
    item.category = data["category"]
    item.main_color = data["main_color"]
    item.secondary_color = data.get("secondary_color")
    item.location = data["location"]

    # Update the count if provided
    if "count" in data:
        item.count = int(data["count"])

    # Check if a new image is uploaded
    if "image_url" in request.files:
        image_file = request.files["image_url"]
        if image_file:
            s3_image_url = upload_image_to_s3_and_get_url(image_file, item.name)
            item.image_url = s3_image_url

    db.session.commit()
    return jsonify({"message": "Clothing item updated!"})


# Delete a clothing item
@main.route("/clothing/<int:item_id>", methods=["DELETE"])
def delete_clothing_item(item_id):
    item = ClothingItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Clothing item deleted!"})


# Search for clothing items
@main.route("/clothing/search", methods=["GET"])
def search_clothing_items():
    query = request.args.get("query", "")
    items = ClothingItem.query.filter(
        (ClothingItem.name.ilike(f"%{query}%"))
        | (ClothingItem.category.ilike(f"%{query}%"))
        | (ClothingItem.main_color.ilike(f"%{query}%"))
        | (ClothingItem.secondary_color.ilike(f"%{query}%"))
    ).all()

    return jsonify(
        [
            {
                "id": item.id,
                "name": item.name,
                "category": item.category,
                "main_color": item.main_color,
                "secondary_color": item.secondary_color,
                "image_url": item.image_url,
                "location": item.location,
            }
            for item in items
        ]
    )


# Update a clothing item's location
@main.route("/clothing/<int:item_id>/move", methods=["PUT"])
def move_clothing_item(item_id):
    data = request.get_json()
    item = ClothingItem.query.get_or_404(item_id)
    item.location = data["location"]  # Update the location
    db.session.commit()
    return jsonify({"message": "Clothing item moved!"})
