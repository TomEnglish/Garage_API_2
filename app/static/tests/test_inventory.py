import unittest
import json
from app import create_app
from app.models import db, Inventory

class InventoryTestCase(unittest.TestCase):
    """This class represents the inventory test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="TestingConfig")
        self.client = self.app.test_client()
        self.inventory_item = {'name': 'Brake Pads', 'price': 50.00}

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_inventory_item_success(self):
        """Test API can create an inventory item (POST request)"""
        # Post the inventory item to the /inventory/ endpoint
        res = self.client.post('/inventory/', data=json.dumps(self.inventory_item), content_type='application/json')
        # Check for a 201 response, indicating the item was created
        self.assertEqual(res.status_code, 201)
        # Load the response data
        json_data = json.loads(res.data)
        # Check that the returned name is correct
        self.assertEqual(json_data['name'], 'Brake Pads')

    def test_create_inventory_item_duplicate(self):
        """Test API cannot create a duplicate inventory item (POST request)"""
        # Post the same item twice
        self.client.post('/inventory/', data=json.dumps(self.inventory_item), content_type='application/json')
        res = self.client.post('/inventory/', data=json.dumps(self.inventory_item), content_type='application/json')
        # Check for a 400 response, indicating a bad request
        self.assertEqual(res.status_code, 400)
        # Load the response data
        json_data = json.loads(res.data)
        # Check that the error message is correct
        self.assertIn('already exists', json_data['error'])

    def test_create_inventory_item_missing_price(self):
        """Test API cannot create an inventory item without a price (POST request)"""
        # Create an item without a price
        item = {'name': 'Brake Pads'}
        # Post the item
        res = self.client.post('/inventory/', data=json.dumps(item), content_type='application/json')
        # Check for a 400 response, indicating a bad request
        self.assertEqual(res.status_code, 400)
        # Load the response data
        json_data = json.loads(res.data)
        # Check that the error message is correct
        self.assertIn("Missing 'price' in request data.", json_data['error'])

    def test_get_inventory_list_success(self):
        """Test API can get a list of inventory items (GET request)"""
        # Post an item to the inventory
        self.client.post('/inventory/', data=json.dumps(self.inventory_item), content_type='application/json')
        # Get the inventory list
        res = self.client.get('/inventory/')
        # Check for a 200 response, indicating success
        self.assertEqual(res.status_code, 200)
        # Load the response data
        json_data = json.loads(res.data)
        # Check that the list contains one item
        self.assertEqual(len(json_data), 1)

    def test_get_inventory_list_empty(self):
        """Test API can handle getting an empty list of inventory items (GET request)"""
        # Get the inventory list without posting any items
        res = self.client.get('/inventory/')
        # Check for a 200 response, indicating success
        self.assertEqual(res.status_code, 200)
        # Load the response data
        json_data = json.loads(res.data)
        # Check that the list is empty
        self.assertEqual(len(json_data), 0)

    def test_update_inventory_success(self):
        """Test API can update an existing inventory item (PUT request)"""
        # Post an item to the inventory
        post_res = self.client.post('/inventory/', data=json.dumps(self.inventory_item), content_type='application/json')
        # Load the response data
        post_json_data = json.loads(post_res.data)
        # Get the id of the item
        item_id = post_json_data['id']
        
        # Create an updated item
        updated_item = {'name': 'New Brake Pads', 'price': 55.00}
        # Put the updated item to the correct endpoint
        res = self.client.put(f'/inventory/{item_id}', data=json.dumps(updated_item), content_type='application/json')
        # Check for a 200 response, indicating success
        self.assertEqual(res.status_code, 200)
        # Load the response data
        json_data = json.loads(res.data)
        # Check that the name and price have been updated
        self.assertEqual(json_data['name'], 'New Brake Pads')
        self.assertEqual(float(json_data['price']), 55.00)

    def test_update_inventory_not_found(self):
        """Test API cannot update a non-existent inventory item (PUT request)"""
        # Create an updated item
        updated_item = {'name': 'New Brake Pads', 'price': 55.00}
        # Try to put the item to an endpoint that does not exist
        res = self.client.put('/inventory/999', data=json.dumps(updated_item), content_type='application/json')
        # Check for a 404 response, indicating that the item was not found
        self.assertEqual(res.status_code, 404)
        # Load the response data
        json_data = json.loads(res.data)
        # Check that the error message is correct
        self.assertIn('inventory not found', json_data['error'])

    def test_delete_inventory_success(self):
        """Test API can delete an existing inventory item (DELETE request)"""
        # Post an item to the inventory
        post_res = self.client.post('/inventory/', data=json.dumps(self.inventory_item), content_type='application/json')
        # Load the response data
        post_json_data = json.loads(post_res.data)
        # Get the id of the item
        item_id = post_json_data['id']

        # Delete the item
        res = self.client.delete(f'/inventory/{item_id}')
        # Check for a 200 response, indicating success
        self.assertEqual(res.status_code, 200)
        # Load the response data
        json_data = json.loads(res.data)
        # Check that the success message is correct
        self.assertIn('successfully deleted', json_data['message'])

    def test_delete_inventory_not_found(self):
        """Test API cannot delete a non-existent inventory item (DELETE request)"""
        # Try to delete an item that does not exist
        res = self.client.delete('/inventory/999')
        # Check for a 404 response, indicating that the item was not found
        self.assertEqual(res.status_code, 404)
        # Load the response data
        json_data = json.loads(res.data)
        # Check that the error message is correct
        self.assertIn('inventory not found', json_data['error'])

if __name__ == "__main__":
    unittest.main()