from .schemas import customer_schema, customers_schema, login_schema
from app.blueprints.service_tickets.schemas import servicetickets_schema
from flask import request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from app.models import Customer, ServiceTickets, db
from . import customers_db
from app.extensions import limiter, cache
from app.utils.util import encode_token, token_required


@customers_db.route("/login", methods=['POST'])
def login():
    try:
        credentials = request.json
        username = credentials['email']
        password = credentials['password']
    except KeyError:
        return jsonify({'messages': 'Invalid payload, expecting username and password'}), 400
    
    query = select(Customer).where(Customer.email == username)
    customer = db.session.execute(query).scalar_one_or_none() 

    if customer and customer.password == password:  # if we have a user associated with the username, validate the password
        auth_token = encode_token(customer.id)
    
        response = {
            "status": "success",
            "message": "Successfully Logged In",
            "auth_token": auth_token
        }

        return jsonify(response), 200
    else:
        return jsonify({'messages': "Invalid email or password"}), 401 
    
@customers_db.route("/login_id/<int:customer_id>", methods=['POST'])
def login_by_id(customer_id):

    try:
        credentials = request.json
        id = customer_id
        password = credentials['password']
    except KeyError:
        return jsonify({'messages': 'Invalid payload, expecting username and password'}), 400
    
    query = select(Customer).where(Customer.id == id)
    customer = db.session.execute(query).scalar_one_or_none() 

    if customer and customer.password == password:  # if we have a user associated with the username, validate the password
        auth_token = encode_token(customer.id)
    
        response = {
            "status": "success",
            "message": "Successfully Logged In",
            "auth_token": auth_token
        }

        return jsonify({"message": f'Customer id: {customer_id}:'},response), 200
    else:
        return jsonify({'messages': "Invalid id or password"}), 401 
    

@customers_db.route("/", methods=['POST'])
@limiter.limit("30 per hour") #Rate limiting a post/create makes sense because we woud not expect a fast rate of customer additions
#possibly something like transactions but not customers.
@cache.cached(timeout=60) 
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Customer).where(Customer.email == customer_data['email']) #Checking our db for a member with this email
    existing_customer = db.session.execute(query).scalars().all()
    if existing_customer:
        return jsonify({"error": "Email already associated with an account."}), 400
    
    new_customer = Customer(**customer_data)
    db.session.add(new_customer)
    db.session.commit()
    return customer_schema.jsonify(new_customer), 201

@customers_db.route("/", methods=['GET'])
@cache.cached(timeout=60) #Caching a customer GET likely makes sense because it would be a frequent query and likey users woud not need upto the second accuracy
def get_customers():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        query = select(Customer)
        result = db.paginate(query, page=page, per_page=per_page)
        return customers_schema.jsonify(result), 200
    except:
        query = select(Customer)
        customers = db.session.execute(query).scalars().all()
        return customers_schema.jsonify(customers)
    

@customers_db.route("/<int:customer_id>", methods=['GET'])
def get_customer(customer_id):
    customer = db.session.get(Customer,customer_id)

    if customer:
        return customer_schema.jsonify(customer), 200
    return jsonify({"error":"Customer Not Found."}), 404


#UPDATE SPECIFIC USER
@customers_db.route("/<int:customer_id>", methods=['PUT'])
def update_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found."}), 404
    
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for key, value in customer_data.items():
        setattr(customer, key, value)

    db.session.commit()
    return customer_schema.jsonify(customer), 200


#DELETE SPECIFIC MEMBER
@customers_db.route("/<int:customer_id>", methods=['DELETE'])
@token_required
def delete_customer(current_customer_id_from_token, customer_id):
    DEFAULT_CUSTOMER_ID = 1 # Define the ID of your default customer

    try:
        target_customer_id = int(customer_id)
    except ValueError:
        return jsonify({"error": "Invalid customer ID format in URL."}), 400

    if target_customer_id == DEFAULT_CUSTOMER_ID:
        return jsonify({"error": "Cannot delete the default customer account."}), 403

    customer_to_delete = db.session.get(Customer, target_customer_id)

    if not customer_to_delete:
        return jsonify({"error": "Customer not found."}), 404

    # Check if the default customer exists
    default_customer = db.session.get(Customer, DEFAULT_CUSTOMER_ID)
    if not default_customer:
        # This is a critical configuration issue.
        # Log this error and inform the admin.
        # For now, prevent deletion to avoid data integrity issues.
        print(f"CRITICAL ERROR: Default customer with ID {DEFAULT_CUSTOMER_ID} not found. Aborting deletion of customer {target_customer_id}.")
        return jsonify({"error": "System configuration error: Default customer not found. Please contact support."}), 500

    # Reassign tickets to the default customer
    # Ensure tickets are loaded if they are lazy-loaded
    if customer_to_delete.tickets: # Check if there are any tickets
        for ticket in list(customer_to_delete.tickets): # Iterate over a copy if modifying the collection
            # ticket.customer_id = DEFAULT_CUSTOMER_ID # Keep this if direct FK assignment is preferred by some style
            ticket.customer = default_customer # Assign the actual customer object
            db.session.add(ticket) # Mark ticket as changed
    
    # Flush the changes to service tickets (UPDATE statements) before deleting the customer
    db.session.flush()

    # Now, delete the customer
    db.session.delete(customer_to_delete)
    db.session.commit()
    
    return jsonify({"message": f'Customer id: {target_customer_id} successfully deleted by user {current_customer_id_from_token}. Tickets reassigned to default customer (ID: {DEFAULT_CUSTOMER_ID}).'}), 200


@customers_db.route("/my-tickets", methods=['GET'])
@token_required
def get_my_tickets(current_customer_id):
    customer = db.session.get(Customer, int(current_customer_id))
    if customer:
        tickets = customer.tickets
        return servicetickets_schema.jsonify(tickets), 200
    else:
        return jsonify({"message": "Customer not found"}), 404
