import requests
from bs4 import BeautifulSoup
from flask import jsonify, request, Blueprint
from models import db, PantryItem, User, ShoppingNote
import traceback
from datetime import datetime
import json
import os
from dotenv import load_dotenv
load_dotenv()
backend = Blueprint('backend', __name__, url_prefix='/backend')


def fetch_image_urls(query):
    api_key = os.getenv('SERPAPI_API_KEY')
    params = {
        "engine": "bing_images",
        "q": ("food" + query),
        "api_key": api_key
    }
    try:
        response = requests.get("https://serpapi.com/search", params=params)
        data = response.json()
        if 'error' in data:
            logging.error(f"API error: {data['error']['message']}")
            return []


        return [image['thumbnail'] for image in data.get('images_results', []) if 'thumbnail' in image]
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return []


@backend.route('/add_pantry_item', methods=['POST'])
def add_pantry_item():
    data = request.get_json()
    if not all(key in data for key in ['name', 'expiry_date', 'user_id', 'quantity']):
        return jsonify({'error': 'Missing data'}), 400


    name = data['name']
    expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d')
    quantity = data['quantity']
    user_id = data['user_id']


    try:
        images = fetch_image_urls(name)
        image_url = images[0] if images else "https://t4.ftcdn.net/jpg/01/74/93/71/360_F_174937114_nrZonPS1Xre7IKYA7EVU715GZGZio0bS.jpg"


        new_item = PantryItem(
            name=name,
            expiry_date=expiry_date,
            quantity=quantity,
            user_id=user_id,
            website_url=image_url
        )
        db.session.add(new_item)
        db.session.commit()
        return jsonify({'message': 'Pantry item added successfully', 'item_id': new_item.id, 'image_url': image_url}), 201
    except Exception as e:
        db.session.rollback()
        logging.error("Error adding pantry item", exc_info=True)  # Use logging with traceback
        return jsonify({'error': str(e)}), 500


@backend.route('/sign_up_user', methods=['POST'])
def add_user():
    data = request.get_json()
    if not all(key in data for key in ['username', 'email', 'password']):
        return jsonify({'error': 'Missing data'}), 400
    new_user = User(username=data['username'], email=data['email'], password=data['password'])
    db.session.add(new_user)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    return jsonify({'message': 'User added successfully', 'user_id': new_user.id}), 201


@backend.route('/delete_pantry_item', methods=['DELETE'])
def delete_pantry_item():
    item_id = request.args.get('item_id')
    if not item_id:
        return jsonify({'error': 'Item ID parameter is required'}), 400
    item = PantryItem.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'message': 'Pantry item deleted successfully'}), 200
    else:
        return jsonify({'message': 'No pantry item found with that ID'}), 404


@backend.route('/search_pantry_item_by_name', methods=['GET'])
def search_pantry_item_by_name():
    name = request.args.get('name')
    user_id = request.args.get('user_id')  # Get user_id from the query parameters
    if not name or not user_id:
        return jsonify({'error': 'Name and user_id parameters are required'}), 400

    items = PantryItem.query.filter(PantryItem.name.ilike(f'%{name}%'), PantryItem.user_id == user_id).all()
    items_data = [{'id': item.id, 'name': item.name, 'expiry_date': item.expiry_date.strftime('%Y-%m-%d'), 'user_id': item.user_id, 'website_url': item.website_url, 'quantity': item.quantity,} for item in items]
    if items:
        return jsonify(items_data), 200
    else:
        return jsonify({'message': 'No pantry items found with that name for the specified user'}), 404


@backend.route('/get_pantry_items_by_user', methods=['GET'])
def get_pantry_items_by_user():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID parameter is required'}), 400
    pantry_items = PantryItem.query.filter_by(user_id=user_id).all()
    items_data = [{'id': item.id, 'name': item.name, 'expiry_date': item.expiry_date.strftime('%Y-%m-%d'), 'quantity': item.quantity, 'website_url': item.website_url} for item in pantry_items]
    return jsonify(items_data), 200


@backend.route('/loginUser', methods=['POST'])
def login_user():
    data = request.get_json()
    if not all(key in data for key in ['email', 'password']):
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if user and user.password == data['password']:
        return jsonify({'user_id': user.id}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 404


@backend.route('/add_note', methods=['POST'])
def add_note():
    data = request.get_json()
    if not all(key in data for key in ['user_id', 'content']):
        return jsonify({'error': 'Missing data'}), 400
    note = ShoppingNote(content=data['content'], user_id=data['user_id'])
    db.session.add(note)
    try:
        db.session.commit()
        return jsonify({'message': 'Note added successfully', 'note_id': note.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@backend.route('/get_notes', methods=['GET'])
def get_notes():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID parameter is required'}), 400
    notes = ShoppingNote.query.filter_by(user_id=user_id).all()
    return jsonify([{'id': note.id, 'content': note.content} for note in notes]), 200


@backend.route('/delete_note', methods=['DELETE'])
def delete_note():
    note_id = request.args.get('note_id')
    if not note_id:
        return jsonify({'error': 'Note ID parameter is required'}), 400
    note = ShoppingNote.query.get(note_id)
    if note:
        db.session.delete(note)
        db.session.commit()
        return jsonify({'message': 'Note deleted successfully'}), 200
    else:
        return jsonify({'message': 'No note found with that ID'}), 404


@backend.route('/update_pantry_item_quantity', methods=['PATCH'])
def update_pantry_item_quantity():
    item_id = request.args.get('item_id')
    new_quantity = request.args.get('quantity')

    if not item_id or not new_quantity:
        return jsonify({'error': 'Item ID and new quantity are required'}), 400

    try:
        new_quantity = int(new_quantity)
        item = PantryItem.query.get(item_id)
        if item:
            item.quantity = new_quantity
            db.session.commit()
            return jsonify({'message': 'Quantity updated successfully', 'item_id': item.id, 'new_quantity': item.quantity}), 200
        else:
            return jsonify({'message': 'Item not found'}), 404
    except ValueError:
        return jsonify({'error': 'Invalid quantity provided'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@backend.route('/get_user_details', methods=['GET'])
def get_user_details():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID parameter is required'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    pantry_item_count = PantryItem.query.filter_by(user_id=user.id).count()
    note_count = ShoppingNote.query.filter_by(user_id=user.id).count()

    user_details = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'pantry_item_count': pantry_item_count,
        'note_count': note_count
    }

    return jsonify(user_details), 200
