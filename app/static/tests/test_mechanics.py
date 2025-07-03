import unittest
import json
from datetime import date
from app import create_app
from app.models import db, Mechanics, Customer, ServiceTickets
from app.utils.util import encode_mec_token

class MechanicsTestCase(unittest.TestCase):
    """This class represents the mechanics test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="TestingConfig")
        self.client = self.app.test_client()
        self.mechanic = {
            'name': 'Test Mechanic',
            'email': 'test@mechanic.com',
            'phone': '1234567890',
            'salary': 50000.00,
            'password': 'password'
        }
        self.mechanic2 = {
            'name': 'Test Mechanic 2',
            'email': 'test2@mechanic.com',
            'phone': '0987654321',
            'salary': 60000.00,
            'password': 'password'
        }

        with self.app.app_context():
            db.create_all()
            # Create a default mechanic
            default_mechanic = Mechanics(id=1, name='Default Mechanic', email='default@mechanic.com', phone='0000000000', salary=40000, password='password')
            db.session.add(default_mechanic)
            db.session.commit()


    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_mechanic_successfully(self):
        """
        Test that a new mechanic can be created successfully through the API.
        It sends a POST request with mechanic data and checks for a 201 status code
        and the new mechanic's name in the response.
        """
        res = self.client.post('/mechanics/', data=json.dumps(self.mechanic), content_type='application/json')
        self.assertEqual(res.status_code, 201)
        self.assertIn('Test Mechanic', str(res.data))

    def test_create_mechanic_with_existing_email(self):
        """
        Test that the API prevents the creation of a mechanic with an email that already exists.
        It first creates a mechanic, then attempts to create another with the same email,
        expecting a 400 status code and a specific error message.
        """
        self.client.post('/mechanics/', data=json.dumps(self.mechanic), content_type='application/json')
        res = self.client.post('/mechanics/', data=json.dumps(self.mechanic), content_type='application/json')
        self.assertEqual(res.status_code, 400)
        self.assertIn('Email already associated with a mechanic', str(res.data))

    def test_get_all_mechanics(self):
        """
        Test that the API can retrieve a list of all mechanics.
        It creates two mechanics and then sends a GET request to the /mechanics/ endpoint,
        expecting a 200 status code and the names of both mechanics in the response.
        """
        self.client.post('/mechanics/', data=json.dumps(self.mechanic), content_type='application/json')
        self.client.post('/mechanics/', data=json.dumps(self.mechanic2), content_type='application/json')
        res = self.client.get('/mechanics/')
        self.assertEqual(res.status_code, 200)
        self.assertIn('Test Mechanic', str(res.data))
        self.assertIn('Test Mechanic 2', str(res.data))

    def test_get_mechanics_by_work_volume(self):
        """
        Test that the API can retrieve a list of mechanics sorted by their work volume (number of service tickets).
        It sets up mechanics with different numbers of associated service tickets and checks if the
        GET /mechanics/volume/ endpoint returns them in the correct order.
        """
        with self.app.app_context():
            m1 = Mechanics(name='Busy Mechanic', email='busy@mechanic.com', phone='111', salary=1, password='p')
            m2 = Mechanics(name='Less Busy Mechanic', email='lessbusy@mechanic.com', phone='222', salary=1, password='p')
            c = Customer(name='c', email='c@c.com', phone='333', password='p')
            db.session.add_all([m1, m2, c])
            db.session.commit()
            st1 = ServiceTickets(vin='123', service_date=date(2025, 1, 1), service_desc='desc', customer_id=c.id)
            st2 = ServiceTickets(vin='456', service_date=date(2025, 1, 1), service_desc='desc', customer_id=c.id)
            st1.mechanics.append(m1)
            st2.mechanics.append(m1)
            db.session.add_all([st1, st2])
            db.session.commit()

        res = self.client.get('/mechanics/volume/')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data[0]['name'], 'Busy Mechanic')
        self.assertEqual(data[1]['name'], 'Default Mechanic') # Default has 0 tickets
        self.assertEqual(data[2]['name'], 'Less Busy Mechanic')


    def test_update_mechanic(self):
        """
        Test that an existing mechanic's details can be updated.
        It creates a mechanic, then sends a PUT request with updated data to the specific mechanic's URL.
        It expects a 200 status code and the updated name in the response.
        """
        res = self.client.post('/mechanics/', data=json.dumps(self.mechanic), content_type='application/json')
        self.assertEqual(res.status_code, 201)
        mechanic_id = json.loads(res.data)['id']
        updated_mechanic = {
            'name': 'Updated Mechanic Name',
            'email': 'updated@mechanic.com',
            'phone': '1111111111',
            'salary': 75000.00,
            'password': 'newpassword'
        }
        res = self.client.put(f'/mechanics/{mechanic_id}', data=json.dumps(updated_mechanic), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertIn('Updated Mechanic Name', str(res.data))

    def test_update_nonexistent_mechanic(self):
        """
        Test that the API returns a 404 error when trying to update a mechanic that does not exist.
        It sends a PUT request to an invalid mechanic ID and checks for the 404 status and error message.
        """
        updated_mechanic = {'name': 'No one'}
        res = self.client.put('/mechanics/1000', data=json.dumps(updated_mechanic), content_type='application/json')
        self.assertEqual(res.status_code, 404)
        self.assertIn('Mechanic not found', str(res.data))

    def test_delete_mechanic(self):
        """
        Test that an existing mechanic can be deleted.
        It creates a mechanic, generates an auth token for them, and then sends a DELETE request
        to the mechanic's URL with the token, expecting a 200 status code and a success message.
        """
        res = self.client.post('/mechanics/', data=json.dumps(self.mechanic), content_type='application/json')
        self.assertEqual(res.status_code, 201)
        mechanic_id = json.loads(res.data)['id']
        
        with self.app.app_context():
            token = encode_mec_token(mechanic_id)

        res = self.client.delete(f'/mechanics/{mechanic_id}', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(res.status_code, 200)
        self.assertIn('successfully deleted', str(res.data))

    def test_delete_nonexistent_mechanic(self):
        """
        Test that the API returns a 404 error when trying to delete a mechanic that does not exist.
        It sends a DELETE request to an invalid mechanic ID and checks for the 404 status and error message.
        """
        with self.app.app_context():
            token = encode_mec_token(1)
        res = self.client.delete('/mechanics/1000', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(res.status_code, 404)
        self.assertIn('Mechanic not found', str(res.data))

    def test_delete_default_mechanic(self):
        """
        Test that the API prevents the deletion of the default mechanic account.
        It attempts to delete the mechanic with ID 1 and expects a 403 status code
        and a specific error message.
        """
        with self.app.app_context():
            token = encode_mec_token(1)
        res = self.client.delete('/mechanics/1', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(res.status_code, 403)
        self.assertIn('Cannot delete the default mechanic account', str(res.data))

    def test_mechanic_login_success(self):
        """
        Test that a mechanic can log in successfully with valid credentials.
        It creates a mechanic and then sends a POST request to the /mechanics/login endpoint
        with the correct email and password, expecting a 200 status code and an auth token.
        """
        self.client.post('/mechanics/', data=json.dumps(self.mechanic), content_type='application/json')
        login_credentials = {
            'email': 'test@mechanic.com',
            'password': 'password'
        }
        res = self.client.post('/mechanics/login', data=json.dumps(login_credentials), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertIn('Successfully Logged In', str(res.data))
        self.assertIn('auth_token', str(res.data))

    def test_mechanic_login_invalid_password(self):
        """
        Test that a mechanic cannot log in with an invalid password.
        It creates a mechanic and then attempts to log in with the correct email but an incorrect password,
        expecting a 401 status code and a specific error message.
        """
        self.client.post('/mechanics/', data=json.dumps(self.mechanic), content_type='application/json')
        login_credentials = {
            'email': 'test@mechanic.com',
            'password': 'wrongpassword'
        }
        res = self.client.post('/mechanics/login', data=json.dumps(login_credentials), content_type='application/json')
        self.assertEqual(res.status_code, 401)
        self.assertIn('Invalid email or password', str(res.data))

    def test_mechanic_login_invalid_email(self):
        """
        Test that a mechanic cannot log in with an email that does not exist.
        It attempts to log in with an unregistered email, expecting a 401 status code
        and a specific error message.
        """
        login_credentials = {
            'email': 'wrong@email.com',
            'password': 'password'
        }
        res = self.client.post('/mechanics/login', data=json.dumps(login_credentials), content_type='application/json')
        self.assertEqual(res.status_code, 401)
        self.assertIn('Invalid email or password', str(res.data))

    def test_mechanic_login_invalid_payload(self):
        """
        Test that the login endpoint handles invalid payloads gracefully.
        It sends a login request with a missing password field and expects a 400 status code
        and a specific error message.
        """
        res = self.client.post('/mechanics/login', data=json.dumps({'email': 'test@mechanic.com'}), content_type='application/json')
        self.assertEqual(res.status_code, 400)
        self.assertIn('Invalid payload', str(res.data))

if __name__ == "__main__":
    unittest.main()