import unittest
import json
from datetime import date
from app import create_app
from app.models import db, ServiceTickets, Mechanics, Customer, Inventory, ServiceInventory

class ServiceTicketsTestCase(unittest.TestCase):
    """This class represents the service tickets test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="TestingConfig")
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            # Create a default customer, mechanic, and inventory for testing
            customer = Customer(name='Test Customer', email='test@customer.com', phone='1234567890', password='password')
            mechanic = Mechanics(name='Test Mechanic', email='test@mechanic.com', phone='0987654321', salary=50000, password='password')
            inventory = Inventory(name='Test Part', price=100.00)
            db.session.add_all([customer, mechanic, inventory])
            db.session.commit()

            self.customer_id = customer.id
            self.mechanic_id = mechanic.id
            self.inventory_id = inventory.id

        self.service_ticket = {
            'vin': '1234567890ABCDEFG',
            'service_date': '2025-07-02',
            'service_desc': 'Test service description',
            'customer_id': self.customer_id
        }

        # Login the test customer to get a token
        login_data = {
            'email': 'test@customer.com',
            'password': 'password'
        }
        res = self.client.post('/customers/login', data=json.dumps(login_data), content_type='application/json')
        self.auth_token = json.loads(res.data)['auth_token']
        self.headers = {
            'Authorization': f'Bearer {self.auth_token}'
        }

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_ticket_successfully(self):
        """
        Test case for creating a new service ticket.
        This test sends a POST request to the '/service_tickets/' endpoint with valid ticket data
        and asserts that the response status code is 201 (Created) and the new ticket's VIN is in the response.
        """
        res = self.client.post('/service_tickets/', data=json.dumps(self.service_ticket), headers=self.headers, content_type='application/json')
        self.assertEqual(res.status_code, 201)
        self.assertIn('1234567890ABCDEFG', str(res.data))

    def test_create_ticket_with_existing_vin(self):
        """
        Test case for creating a service ticket with a duplicate VIN.
        This test first creates a service ticket and then attempts to create another ticket with the same VIN.
        It asserts that the second request fails with a 400 status code and an appropriate error message.
        """
        self.client.post('/service_tickets/', data=json.dumps(self.service_ticket), headers=self.headers, content_type='application/json')
        res = self.client.post('/service_tickets/', data=json.dumps(self.service_ticket), headers=self.headers, content_type='application/json')
        self.assertEqual(res.status_code, 400)
        self.assertIn('already exists', str(res.data))

    def test_get_all_servicetickets(self):
        """
        Test case for retrieving all service tickets.
        This test creates a service ticket and then sends a GET request to the '/service_tickets/' endpoint.
        It asserts that the response status code is 200 (OK) and that the created ticket's VIN is in the response data.
        """
        self.client.post('/service_tickets/', data=json.dumps(self.service_ticket), headers=self.headers, content_type='application/json')
        res = self.client.get('/service_tickets/')
        self.assertEqual(res.status_code, 200)
        self.assertIn('1234567890ABCDEFG', str(res.data))

    def test_assign_mechanic_successfully(self):
        """
        Test case for assigning a mechanic to a service ticket.
        This test creates a service ticket, then sends a PUT request to assign a mechanic to it.
        It asserts that the response status code is 200 (OK) and that a success message is returned.
        """
        res = self.client.post('/service_tickets/', data=json.dumps(self.service_ticket), headers=self.headers, content_type='application/json')
        ticket_id = json.loads(res.data)['id']
        
        res = self.client.put(f'/service_tickets/{ticket_id}/assign-mechanic/{self.mechanic_id}')
        self.assertEqual(res.status_code, 200)
        self.assertIn('assigned to Ticket', str(res.data))

    def test_assign_mechanic_to_nonexistent_ticket(self):
        """
        Test case for assigning a mechanic to a non-existent service ticket.
        This test sends a PUT request to assign a mechanic to a ticket ID that does not exist.
        It asserts that the request fails with a 404 status code and a 'Ticket not found' message.
        """
        res = self.client.put(f'/service_tickets/999/assign-mechanic/{self.mechanic_id}')
        self.assertEqual(res.status_code, 404)
        self.assertIn('Ticket not found', str(res.data))

    def test_remove_mechanic_successfully(self):
        """
        Test case for removing a mechanic from a service ticket.
        This test creates a ticket, assigns a mechanic, and then sends a PUT request to remove the mechanic.
        It asserts that the removal is successful with a 200 status code.
        """
        res = self.client.post('/service_tickets/', data=json.dumps(self.service_ticket), headers=self.headers, content_type='application/json')
        ticket_id = json.loads(res.data)['id']
        self.client.put(f'/service_tickets/{ticket_id}/assign-mechanic/{self.mechanic_id}')
        
        res = self.client.put(f'/service_tickets/{ticket_id}/remove-mechanic/{self.mechanic_id}')
        self.assertEqual(res.status_code, 200)
        self.assertIn('removed from Ticket', str(res.data))

    def test_remove_mechanic_from_nonexistent_ticket(self):
        """
        Test case for removing a mechanic from a non-existent service ticket.
        This test sends a PUT request to remove a mechanic from a ticket ID that does not exist.
        It asserts that the request fails with a 404 status code and a 'Ticket not found' message.
        """
        res = self.client.put(f'/service_tickets/999/remove-mechanic/{self.mechanic_id}')
        self.assertEqual(res.status_code, 404)
        self.assertIn('Ticket not found', str(res.data))

    def test_edit_mechanic_on_ticket(self):
        """
        Test case for editing the mechanics assigned to a service ticket.
        This test first adds a mechanic to a ticket and verifies the addition.
        Then, it removes the mechanic and verifies the removal, checking the count of assigned mechanics.
        """
        res = self.client.post('/service_tickets/', data=json.dumps(self.service_ticket), headers=self.headers, content_type='application/json')
        ticket_id = json.loads(res.data)['id']
        
        edit_data = {
            "add_mechanic_ids": [self.mechanic_id],
            "remove_mechanic_ids": []
        }
        res = self.client.put(f'/service_tickets/{ticket_id}/edit/', data=json.dumps(edit_data), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(json.loads(res.data)['mechanics']), 1)

        edit_data = {
            "add_mechanic_ids": [],
            "remove_mechanic_ids": [self.mechanic_id]
        }
        res = self.client.put(f'/service_tickets/{ticket_id}/edit/', data=json.dumps(edit_data), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(json.loads(res.data)['mechanics']), 0)

    def test_edit_mechanic_on_nonexistent_ticket(self):
        """
        Test case for editing mechanics on a non-existent service ticket.
        This test sends a PUT request to edit mechanics for a ticket ID that does not exist.
        It asserts that the server returns a 404 Not Found error.
        """
        edit_data = {"add_mechanic_ids": [self.mechanic_id], "remove_mechanic_ids": []}
        res = self.client.put('/service_tickets/999/edit/', data=json.dumps(edit_data), content_type='application/json')
        self.assertEqual(res.status_code, 404)


    def test_edit_inventory_on_ticket(self):
        """
        Test case for managing inventory items on a service ticket.
        This comprehensive test covers adding an inventory item, updating its quantity, and finally removing it.
        Each step asserts that the API responds correctly and the inventory state is as expected.
        """
        res = self.client.post('/service_tickets/', data=json.dumps(self.service_ticket), headers=self.headers, content_type='application/json')
        ticket_id = json.loads(res.data)['id']

        # Add an item
        edit_data = {
            "items_to_add_or_update": [{"inventory_id": self.inventory_id, "quantity": 2}]
        }
        res = self.client.put(f'/service_tickets/{ticket_id}/edit_inventory/', data=json.dumps(edit_data), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(json.loads(res.data)['inventory']), 1)
        self.assertEqual(json.loads(res.data)['inventory'][0]['quantity'], 2)

        # Update an item
        edit_data = {
            "items_to_add_or_update": [{"inventory_id": self.inventory_id, "quantity": 5}]
        }
        res = self.client.put(f'/service_tickets/{ticket_id}/edit_inventory/', data=json.dumps(edit_data), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.data)['inventory'][0]['quantity'], 5)

        # Remove an item
        edit_data = {
            "remove_inventory_ids": [self.inventory_id]
        }
        res = self.client.put(f'/service_tickets/{ticket_id}/edit_inventory/', data=json.dumps(edit_data), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(json.loads(res.data)['inventory']), 0)

    def test_edit_inventory_on_nonexistent_ticket(self):
        """
        Test case for editing inventory on a non-existent service ticket.
        This test sends a PUT request to edit inventory for a ticket ID that does not exist.
        It asserts that the request fails with a 404 status code and a 'Service ticket not found' message.
        """
        edit_data = {"items_to_add_or_update": [{"inventory_id": self.inventory_id, "quantity": 1}]}
        res = self.client.put('/service_tickets/999/edit_inventory/', data=json.dumps(edit_data), content_type='application/json')
        self.assertEqual(res.status_code, 404)
        self.assertIn("Service ticket not found", str(res.data))

if __name__ == "__main__":
    unittest.main()