from . import tickets_db
from flask import request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from app.models import ServiceTickets, Mechanics, Inventory, ServiceInventory, db
from .schemas import servicetickets_schema, serviceticket_schema
from .schemas import edit_service_ticket_schema, edit_service_ticket_inventory_schema
from app.extensions import limiter, cache
from app.utils.util import token_required



# POST '/': Pass in all the required information to create the service_ticket.
@tickets_db.route("/", methods=['POST'])
@token_required
@limiter.limit("20/hour") #how many tickets per day or hour would be reasonabe...not too many
def create_ticket(current_customer_id):
    try:
        ticket_data = serviceticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # Check if a ticket with the same VIN already exists
    query = select(ServiceTickets).where(ServiceTickets.vin == ticket_data.vin)
    existing_ticket = db.session.execute(query).scalars().first() # Use .first() as VIN is unique
    if existing_ticket:
        return jsonify({"error": f"Service ticket with VIN {ticket_data.vin} already exists"}), 400
    
    ticket_data.customer_id = current_customer_id
    new_ticket = ticket_data
    db.session.add(new_ticket)
    db.session.commit()
    return serviceticket_schema.jsonify(new_ticket), 201


# PUT '/<ticket_id>/assign-mechanic/<mechanic-id>: Adds a relationship between a service ticket and the mechanics. (Reminder: use your relationship attributes! They allow you the treat the relationship like a list, able to append a Mechanic to the mechanics list).
@tickets_db.route("/<ticket_id>/assign-mechanic/<mechanic_id>", methods=['PUT'])
def assign_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTickets, ticket_id)
    mechanic = db.session.get(Mechanics, mechanic_id)

    if not ticket:
        return jsonify({"error": "Ticket not found."}), 404
    
    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404
    
    ticket.mechanics.append(mechanic)
    db.session.commit()
    serialized_ticket = serviceticket_schema.dump(ticket)
    message = f"Mechanic {mechanic.name} (ID: {mechanic.id}) assigned to Ticket ID: {ticket.id}"
    return jsonify(message=message, ticket=serialized_ticket), 200
 
# PUT '/<ticket_id>/remove-mechanic/<mechanic-id>: Adds a relationship between a service ticket and the mechanics. (Reminder: use your relationship attributes! They allow you the treat the relationship like a list, able to append a Mechanic to the mechanics list).
@tickets_db.route("/<ticket_id>/remove-mechanic/<mechanic_id>", methods=['PUT'])
def remove_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTickets, ticket_id)
    mechanic = db.session.get(Mechanics, mechanic_id)

    if not ticket:
        return jsonify({"error": "Ticket not found."}), 404
    
    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404
    
    ticket.mechanics.remove(mechanic)
    db.session.commit()
    serialized_ticket = serviceticket_schema.dump(ticket)
    message = f"Mechanic {mechanic.name} (ID: {mechanic.id}) removed from Ticket ID: {ticket.id}"
    return jsonify(message=message, ticket=serialized_ticket), 200


# GET '/': Retrieves all service tickets.

@tickets_db.route('/', methods=['GET'])
@cache.cached(timeout=60)#A Get of ALl tickets is ikey something like a dashboard would pull from frequently
def get_all_servicetickets():
    query = select(ServiceTickets)
    
    tickets = db.session.execute(query).scalars().all()

    return servicetickets_schema.jsonify(tickets), 200

 
 # PUT '/<int:ticket_id>/edit' : Takes in remove_ids, and add_ids
# Use id's to look up the mechanic to append or remove them from the ticket.mechanics list
@tickets_db.route("/<int:ticket_id>/edit/", methods=['PUT'])
def edit_mechanic(ticket_id):

    try:
        ticket_updates = edit_service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(ServiceTickets).where(ServiceTickets.id == ticket_id) # Corrected line

    result = db.session.execute(query).scalars().first()

    if not result:
        return jsonify({"error": "Service ticket not found"}), 404
    
    for mechanic_id in ticket_updates["add_mechanic_ids"]:
        query = select(Mechanics).where(Mechanics.id == mechanic_id)
        mechanic = db.session.execute(query).scalars().first()

        if mechanic and mechanic not in result.mechanics:
            result.mechanics.append(mechanic)

    for mechanic_id in ticket_updates["remove_mechanic_ids"]:
        query = select(Mechanics).where(Mechanics.id == mechanic_id)
        mechanic = db.session.execute(query).scalars().first()

        if mechanic and mechanic in result.mechanics:
            result.mechanics.remove(mechanic)

    db.session.commit()
    return serviceticket_schema.jsonify(result), 200


#add a single part to an existing Service Ticket.
@tickets_db.route("/<int:ticket_id>/edit_inventory/", methods=['PUT'])
def edit_inventory(ticket_id):

    try:
        ticket_updates = edit_service_ticket_inventory_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

 
    service_ticket = db.session.get(ServiceTickets, ticket_id)

    if not service_ticket:
        return jsonify({"error": "Service ticket not found"}), 404
    
    # Add or update inventory items
    for item_data in ticket_updates.get("items_to_add_or_update", []):
        inventory_id = item_data.get("inventory_id")
        quantity = item_data.get("quantity")

        if inventory_id is None or quantity is None:
            continue

        inventory_item = db.session.get(Inventory, inventory_id)
        if inventory_item:
            existing_si_item = db.session.execute(
                select(ServiceInventory).where(
                    ServiceInventory.service_ticket_id == service_ticket.id,
                    ServiceInventory.inventory_id == inventory_item.id
                )
            ).scalars().first()

            if existing_si_item:
                # Update quantity if item already associated
                existing_si_item.quantity = quantity
            else:
                # Add new association with specified quantity
                new_service_inventory = ServiceInventory(
                    service_ticket_id=service_ticket.id,
                    inventory_id=inventory_item.id,
                    quantity=quantity
                )
                db.session.add(new_service_inventory)

    # Remove inventory items
    for inventory_id in ticket_updates.get("remove_inventory_ids", []):
        service_inventory_to_remove = db.session.execute(
            select(ServiceInventory).where(
                ServiceInventory.service_ticket_id == service_ticket.id,
                ServiceInventory.inventory_id == inventory_id
            )
        ).scalars().first()
        
        if service_inventory_to_remove:
            db.session.delete(service_inventory_to_remove)


    db.session.commit()
   
    updated_ticket = db.session.get(ServiceTickets, ticket_id)
    return serviceticket_schema.jsonify(updated_ticket), 200