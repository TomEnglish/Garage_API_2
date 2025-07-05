import unittest
import json
from app import create_app
from app.models import db, Customer, ServiceTickets
from app.utils.util import encode_token
from datetime import date

class TestCustomers(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            # Create a default customer for FK constraints
            default_customer = Customer(id=1, name='Default Customer', email='default@example.com', phone='0000000000', password='password')
            db.session.add(default_customer)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_customer_success(self):
        # Test successful creation of a new customer
        with self.app.app_context():
            data = {'name': 'John Doe', 'email': 'john.doe@example.com', 'phone': '1234567890', 'password': 'password'}
            response = self.client.post('/customers/', data=json.dumps(data), content_type='application/json')
            self.assertEqual(response.status_code, 201)
            self.assertIn('john.doe@example.com', str(response.data))

    def test_create_customer_duplicate_email(self):
        # Test that creating a customer with a duplicate email fails
        with self.app.app_context():
            customer = Customer(name='Jane Doe', email='jane.doe@example.com', phone='0987654321', password='password')
            db.session.add(customer)
            db.session.commit()
            data = {'name': 'Jane Doe', 'email': 'jane.doe@example.com', 'phone': '0987654321', 'password': 'password'}
            response = self.client.post('/customers/', data=json.dumps(data), content_type='application/json')
            self.assertEqual(response.status_code, 400)
            self.assertIn('Email already associated with an account', str(response.data))

    def test_get_customers_success(self):
        # Test successful retrieval of all customers
        with self.app.app_context():
            response = self.client.get('/customers/')
            self.assertEqual(response.status_code, 200)

    def test_get_customers_with_pagination_success(self):
        # Test successful retrieval of customers with pagination
        with self.app.app_context():
            response = self.client.get('/customers/?page=1&per_page=1')
            self.assertEqual(response.status_code, 200)

    def test_get_customer_success(self):
        # Test successful retrieval of a single customer by ID
        with self.app.app_context():
            customer = Customer(name='Test Customer', email='test@test.com', phone='1111111111', password='password')
            db.session.add(customer)
            db.session.commit()
            response = self.client.get(f'/customers/{customer.id}')
            self.assertEqual(response.status_code, 200)
            self.assertIn('test@test.com', str(response.data))

    def test_get_customer_not_found(self):
        # Test that retrieving a non-existent customer returns a 404 error
        with self.app.app_context():
            response = self.client.get('/customers/999')
            self.assertEqual(response.status_code, 404)
            self.assertIn('Customer Not Found', str(response.data))

    def test_update_customer_success(self):
        # Test successful update of a customer's information
        with self.app.app_context():
            customer = Customer(name='Update Test', email='update@test.com', phone='2222222222', password='password')
            db.session.add(customer)
            db.session.commit()
            data = {'name': 'Updated Name', 'email': 'update@test.com', 'phone': '2222222222', 'password': 'password'}
            response = self.client.put(f'/customers/{customer.id}', data=json.dumps(data), content_type='application/json')
            self.assertEqual(response.status_code, 200)
            self.assertIn('Updated Name', str(response.data))

    def test_update_customer_not_found(self):
        # Test that updating a non-existent customer returns a 404 error
        with self.app.app_context():
            data = {'name': 'Updated Name'}
            response = self.client.put('/customers/999', data=json.dumps(data), content_type='application/json')
            self.assertEqual(response.status_code, 404)
            self.assertIn('Customer not found', str(response.data))

    def test_delete_customer_success(self):
        # Test successful deletion of a customer
        with self.app.app_context():
            customer = Customer(name='Delete Test', email='delete@test.com', phone='3333333333', password='password')
            db.session.add(customer)
            db.session.commit()
            token = encode_token(customer.id)
            headers = {'Authorization': f'Bearer {token}'}
            response = self.client.delete(f'/customers/{customer.id}', headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertIn('successfully deleted', str(response.data))

    def test_delete_customer_not_found(self):
        # Test that deleting a non-existent customer returns a 404 error
        with self.app.app_context():
            token = encode_token(1)
            headers = {'Authorization': f'Bearer {token}'}
            response = self.client.delete('/customers/999', headers=headers)
            self.assertEqual(response.status_code, 404)
            self.assertIn('Customer not found', str(response.data))
            
    def test_delete_default_customer_fail(self):
        # Test that deleting the default customer is not allowed
        with self.app.app_context():
            token = encode_token(1)
            headers = {'Authorization': f'Bearer {token}'}
            response = self.client.delete('/customers/1', headers=headers)
            self.assertEqual(response.status_code, 403)
            self.assertIn("Cannot delete the default customer account.", str(response.data))

    def test_login_success(self):
        # Test successful customer login with valid credentials
        with self.app.app_context():
            customer = Customer(name='Login Test', email='login@test.com', phone='4444444444', password='password')
            db.session.add(customer)
            db.session.commit()
            data = {'email': 'login@test.com', 'password': 'password'}
            response = self.client.post('/customers/login', data=json.dumps(data), content_type='application/json')
            self.assertEqual(response.status_code, 200)
            self.assertIn('auth_token', str(response.data))

    def test_login_invalid_credentials(self):
        # Test that login fails with invalid credentials
        with self.app.app_context():
            data = {'email': 'wrong@test.com', 'password': 'wrongpassword'}
            response = self.client.post('/customers/login', data=json.dumps(data), content_type='application/json')
            self.assertEqual(response.status_code, 401)
            self.assertIn('Invalid email or password', str(response.data))

    def test_login_by_id_success(self):
        # Test successful customer login by ID
        with self.app.app_context():
            customer = Customer(name='Login ID Test', email='loginid@test.com', phone='5555555555', password='password')
            db.session.add(customer)
            db.session.commit()
            data = {'password': 'password'}
            response = self.client.post(f'/customers/login_id/{customer.id}', data=json.dumps(data), content_type='application/json')
            self.assertEqual(response.status_code, 200)
            self.assertIn('auth_token', str(response.data))

    def test_login_by_id_invalid_password(self):
        # Test that login by ID fails with an invalid password
        with self.app.app_context():
            customer = Customer(name='Login ID Fail', email='loginidfail@test.com', phone='6666666666', password='password')
            db.session.add(customer)
            db.session.commit()
            data = {'password': 'wrongpassword'}
            response = self.client.post(f'/customers/login_id/{customer.id}', data=json.dumps(data), content_type='application/json')
            self.assertEqual(response.status_code, 401)
            self.assertIn('Invalid id or password', str(response.data))

    def test_get_my_tickets_success(self):
        # Test successful retrieval of a customer's own service tickets
        with self.app.app_context():
            customer = Customer(name='My Tickets Test', email='mytickets@test.com', phone='7777777777', password='password')
            db.session.add(customer)
            db.session.commit()

            ticket = ServiceTickets(
                vin="TestVIN123",
                service_date=date(2023, 1, 1),
                service_desc="Test service",
                customer_id=customer.id
            )
            db.session.add(ticket)
            db.session.commit()

            token = encode_token(customer.id)
            headers = {'Authorization': f'Bearer {token}'}
            response = self.client.get('/customers/my-tickets', headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertIn("TestVIN123", str(response.data))

    def test_get_my_tickets_unauthorized(self):
        # Test that retrieving tickets without authorization fails
        with self.app.app_context():
            response = self.client.get('/customers/my-tickets')
            self.assertEqual(response.status_code, 401)
            self.assertIn('Authorization header is missing', str(response.data))

if __name__ == '__main__':
    unittest.main()