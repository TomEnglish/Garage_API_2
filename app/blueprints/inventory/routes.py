from . import inventory_db
from flask import request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from app.models import Inventory, db
from .schemas import inventory_item_schema, inventory_schema



@inventory_db.route("/", methods=['POST'])

def create_inventory_item():
    try:
        inventory_data = inventory_item_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    if 'price' not in inventory_data:
        return jsonify({"error": "Missing 'price' in request data."}), 400

    query = select(Inventory).where(Inventory.name == inventory_data['name'])
    existing_inventory_item = db.session.execute(query).scalars().first()
    if existing_inventory_item:
        return jsonify({"error": f"Inventory item with name {inventory_data['name']} already exists."}), 400
    
    new_inventory_item = Inventory(**inventory_data)
    db.session.add(new_inventory_item)
    db.session.commit()
    return inventory_item_schema.jsonify(new_inventory_item), 201



@inventory_db.route('/', methods=['GET'])
def get_inventory_list():
    query = select(Inventory)
    # Placeholder: return actual data
    
    inventorys = db.session.execute(query).scalars().all()
    return inventory_schema.jsonify(inventorys), 200


#UPDATE SPECIFIC EMPLOYEE/MECHANIC
@inventory_db.route("/<int:inventory_id>", methods=['PUT'])
def update_inventory(inventory_id):
    print(f"DEBUG: update_inventory called for ID: {inventory_id}, Method: {request.method}") # Add this line
    item = db.session.get(Inventory, inventory_id)

    if not item:
        return jsonify({"error": "inventory not found."}), 404
    
    try:
        inventory_data = inventory_item_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for key, value in inventory_data.items():
        setattr(item, key, value)

    db.session.commit()
    return inventory_item_schema.jsonify(item), 200

#DELETE SPECIFIC MEMBER
@inventory_db.route("/<int:inventory_id>", methods=['DELETE'])
def delete_inventory(inventory_id):
    inventory_item = db.session.get(Inventory, inventory_id)

    if not inventory_item:
        return jsonify({"error": "inventory not found."}), 404
    
    db.session.delete(inventory_item)
    db.session.commit()
    return jsonify({"message": f'inventory id: {inventory_id}, successfully deleted.'}), 200