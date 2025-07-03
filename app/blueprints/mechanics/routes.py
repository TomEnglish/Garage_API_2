# Placeholder for DEFAULT_CUSTOMER_ID to resolve NameError
DEFAULT_CUSTOMER_ID = 1 # Or any appropriate default value
from . import mechanics_db
from flask import request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from app.models import Mechanics, db
from .schemas import mechanic_schema, mechanics_schema
from app.utils.util import encode_mec_token, mec_token_required



@mechanics_db.route("/login", methods=['POST'])
def login():
    try:
        credentials = request.json
        username = credentials['email']
        password = credentials['password']
    except KeyError:
        return jsonify({'messages': 'Invalid payload, expecting username and password'}), 400
    
    query = select(Mechanics).where(Mechanics.email == username)
    customer = db.session.execute(query).scalar_one_or_none() 

    if customer and customer.password == password:  # if we have a user associated with the username, validate the password
        auth_token = encode_mec_token(customer.id)
    
        response = {
            "status": "success",
            "message": "Successfully Logged In",
            "auth_token": auth_token
        }

        return jsonify(response), 200
    else:
        return jsonify({'messages': "Invalid email or password"}), 401 


@mechanics_db.route("/", methods=['POST'])
#@mec_token_required
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Mechanics).where(Mechanics.email == mechanic_data['email']) #Checking our db for a member with this email
    existing_mechanic = db.session.execute(query).scalars().all()
    if existing_mechanic:
        return jsonify({"error": "Email already associated with a mechanic."}), 400
    
    new_mechanic = Mechanics(**mechanic_data)
    db.session.add(new_mechanic)
    db.session.commit()
    return mechanic_schema.jsonify(new_mechanic), 201



@mechanics_db.route('/', methods=['GET'])
def get_mechanics_list():
    query = select(Mechanics)
    # Placeholder: return actual data
    
    mechanics = db.session.execute(query).scalars().all()
    return mechanics_schema.jsonify(mechanics), 200

@mechanics_db.route('/volume/', methods=['GET'])
def get_mechanics_list_by_work_vol():
    query = select(Mechanics)
    # Placeholder: return actual data
    
    mechanics = db.session.execute(query).scalars().all()
    mechanics.sort(key=lambda mechanics:len(mechanics.service_tickets), reverse=True)

    return mechanics_schema.jsonify(mechanics), 200


#UPDATE SPECIFIC EMPLOYEE/MECHANIC
@mechanics_db.route("/<int:mechanic_id>", methods=['PUT'])
#@mec_token_required
def update_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanics, mechanic_id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404
    
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for key, value in mechanic_data.items():
        setattr(mechanic, key, value)

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200

#DELETE SPECIFIC MEMBER
# @mechanics_db.route("/<int:mechanic_id>", methods=['DELETE'])
# @mec_token_required
# def delete_mechanic(mechanic_id):
#     mechanic = db.session.get(Mechanics, mechanic_id)

#     if not mechanic:
#         return jsonify({"error": "Mechanic not found."}), 404
    
#     db.session.delete(mechanic)
#     db.session.commit()
#     return jsonify({"message": f'Mechanic id: {mechanic_id}, successfully deleted.'}), 200

#DELETE SPECIFIC MEMBER
@mechanics_db.route("/<int:mechanic_id>", methods=['DELETE'])
@mec_token_required
def delete_mechanic(current_mechanic_id_from_token, mechanic_id):
    DEFAULT_MECHANIC_ID = 1 # Define the ID of your default customer

    try:
        target_mechanic_id = int(mechanic_id)
    except ValueError:
        return jsonify({"error": "Invalid mechanic ID format in URL."}), 400

    if target_mechanic_id == DEFAULT_MECHANIC_ID:
        return jsonify({"error": "Cannot delete the default mechanic account."}), 403

    mechanic_to_delete = db.session.get(Mechanics, target_mechanic_id)

    if not mechanic_to_delete:
        return jsonify({"error": "Mechanic not found."}), 404


    default_mechanic = db.session.get(Mechanics, DEFAULT_MECHANIC_ID)
    if not default_mechanic:
       print(f"CRITICAL ERROR: Default mechanic with ID {DEFAULT_MECHANIC_ID} not found. Aborting deletion of customer {target_mechanic_id}.")
       return jsonify({"error": "System configuration error: Default customer not found. Please contact support."}), 500

    # if mechanic_to_delete.tickets: # Check if there are any tickets
    #     for ticket in list(mechanic_to_delete.tickets): # Iterate over a copy if modifying the collection
           
    #         ticket.mechanic = default_mechanic # Assign the actual customer object
    #         db.session.add(ticket) # Mark ticket as changed
    
    db.session.flush()

    db.session.delete(mechanic_to_delete)
    db.session.commit()
    
    return jsonify({"message": f'Mechanic id: {target_mechanic_id} successfully deleted by user {current_mechanic_id_from_token}.'}), 200
