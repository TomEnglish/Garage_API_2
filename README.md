# MyGarage API

A comprehensive RESTful API for managing an auto garage business, including customer management, inventory tracking, mechanic assignments, and service ticket processing.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Authentication](#authentication)
- [Rate Limiting](#rate-limiting)
- [Caching](#caching)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)

## Overview

MyGarage API is a Flask-based web application that provides a complete solution for managing auto garage operations. It allows garage owners to manage customers, track inventory, assign mechanics to service tickets, and maintain service records. The API follows RESTful principles and uses JWT-based authentication for secure access to protected endpoints.

## Features

### Customer Management
- Customer registration and authentication
- Customer profile management (view, update, delete)
- Customer service ticket history
- Pagination support for customer listings

### Mechanic Management
- Mechanic registration and authentication
- Mechanic profile management
- Work volume tracking (mechanics sorted by number of service tickets)
- Secure deletion with default mechanic fallback

### Inventory Management
- Inventory item CRUD operations
- Price tracking for parts and supplies
- Inventory association with service tickets

### Service Ticket Management
- Service ticket creation and management
- Mechanic assignment to service tickets
- Inventory item association with service tickets
- Customer ticket history

### Additional Features
- JWT-based authentication for customers and mechanics
- Rate limiting for API endpoints
- Response caching for frequently accessed data
- Comprehensive API documentation with Swagger UI
- Postman collection for easy API testing

## Technology Stack

- **Backend**: Flask 3.0.3
- **Database**: SQLAlchemy 2.0.35 with MySQL/PostgreSQL support
- **Authentication**: JWT (JSON Web Tokens) using PyJWT
- **Serialization**: Marshmallow with Flask-Marshmallow
- **API Documentation**: Swagger UI
- **Rate Limiting**: Flask-Limiter
- **Caching**: Flask-Caching
- **WSGI Server**: Gunicorn

## Installation

### Prerequisites
- Python 3.8+
- MySQL or PostgreSQL database
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Garage_API-main.git
cd Garage_API-main
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials and secret key
```

5. Initialize the database:
```bash
python flask_app.py
```

## Configuration

The application supports multiple environments through configuration classes:

### Development Configuration
```python
class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:Password1@localhost/garage_db'
    DEBUG = True
```

### Production Configuration
```python
class ProductionConfig:
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
```

### Environment Variables
- `SQLALCHEMY_DATABASE_URI`: Database connection string
- `SECRET_KEY`: Secret key for JWT encoding
- `PORT`: Port number for the application (default: 5000)

## API Documentation

### Swagger UI
The API documentation is available through Swagger UI at `/api/docs` when the application is running.

### Postman Collection
A Postman collection (`MyGarage.postman_collection.json`) is provided for easy API testing.

### API Endpoints

#### Customer Endpoints
- `POST /customers/login` - Customer login
- `POST /customers/login_id/{customer_id}` - Customer login by ID
- `POST /customers/` - Create a new customer
- `GET /customers/` - Get all customers (with pagination)
- `GET /customers/{customer_id}` - Get customer by ID
- `PUT /customers/{customer_id}` - Update customer
- `DELETE /customers/{customer_id}` - Delete customer (requires authentication)
- `GET /customers/my-tickets` - Get customer's service tickets (requires authentication)

#### Mechanic Endpoints
- `POST /mechanics/login` - Mechanic login
- `POST /mechanics/` - Create a new mechanic
- `GET /mechanics/` - Get all mechanics
- `GET /mechanics/volume/` - Get mechanics sorted by work volume
- `PUT /mechanics/{mechanic_id}` - Update mechanic
- `DELETE /mechanics/{mechanic_id}` - Delete mechanic (requires authentication)

#### Inventory Endpoints
- `POST /inventory/` - Create inventory item
- `GET /inventory/` - Get all inventory items
- `PUT /inventory/{inventory_id}` - Update inventory item
- `DELETE /inventory/{inventory_id}` - Delete inventory item

#### Service Ticket Endpoints
- `POST /service_tickets/` - Create service ticket (requires authentication)
- `GET /service_tickets/` - Get all service tickets
- `PUT /service_tickets/{ticket_id}/assign-mechanic/{mechanic_id}` - Assign mechanic to ticket
- `PUT /service_tickets/{ticket_id}/remove-mechanic/{mechanic_id}` - Remove mechanic from ticket
- `PUT /service_tickets/{ticket_id}/edit/` - Edit mechanics on ticket
- `PUT /service_tickets/{ticket_id}/edit_inventory/` - Edit inventory on ticket

## Database Schema

### Customers Table
- `id` (Primary Key)
- `name` (String, 225 characters, required)
- `email` (String, 360 characters, required, unique)
- `phone` (String, 20 characters, unique)
- `password` (String, 225 characters, required)

### Mechanics Table
- `id` (Primary Key)
- `name` (String, 225 characters, required)
- `email` (String, 360 characters, required, unique)
- `phone` (String, 20 characters, unique)
- `salary` (Numeric, 10,2, required)
- `password` (String, 225 characters, required)

### Inventory Table
- `id` (Primary Key)
- `name` (String, 225 characters, required)
- `price` (Numeric, 10,2, required)

### Service Tickets Table
- `id` (Primary Key)
- `vin` (String, 30 characters, required, unique)
- `service_date` (Date, required)
- `service_desc` (String, 300 characters)
- `customer_id` (Foreign Key to Customers.id, required)

### Service Inventory Table (Junction Table)
- `id` (Primary Key)
- `service_ticket_id` (Foreign Key to ServiceTickets.id, required)
- `inventory_id` (Foreign Key to Inventory.id, required)
- `quantity` (Integer, required)

### Service Mechanics Table (Junction Table)
- `service_ticket_id` (Foreign Key to ServiceTickets.id, Primary Key)
- `mechanic_id` (Foreign Key to Mechanics.id, Primary Key)

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Two types of tokens are supported:

### Customer Authentication
- Customers can authenticate using email/password or customer_id/password
- Tokens are issued with a 1-hour expiration time
- Protected customer endpoints require a valid JWT token in the Authorization header

### Mechanic Authentication
- Mechanics authenticate using email/password
- Tokens are issued with a 1-hour expiration time
- Protected mechanic endpoints require a valid JWT token in the Authorization header

### Usage Example
```python
# After login, include the token in subsequent requests
headers = {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse:

- Default limits: 200 requests per day, 30 per hour
- Customer creation: 30 requests per hour
- Service ticket creation: 20 requests per hour

Rate limiting is implemented using Flask-Limiter with IP-based tracking.

## Caching

Frequently accessed data is cached to improve performance:

- Customer listings: 60-second cache
- All service tickets: 60-second cache

Caching is implemented using Flask-Caching with SimpleCache backend.

## Testing

The application includes test suites for all major components:

- `app/static/tests/test_customers.py` - Customer endpoint tests
- `app/static/tests/test_mechanics.py` - Mechanic endpoint tests
- `app/static/tests/test_inventory.py` - Inventory endpoint tests
- `app/static/tests/test_service_tickets.py` - Service ticket endpoint tests

### Running Tests
```bash
# Run all tests
python -m pytest app/static/tests/

# Run specific test file
python -m pytest app/static/tests/test_customers.py
```

## Deployment

### Local Development
```bash
python flask_app.py
```

### Production with Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 flask_app:app
```

### Render Deployment
The application is configured for deployment on Render with the following settings:

- Host: `0.0.0.0`
- Port: From environment variable `PORT` (default: 5000)
- Debug mode: Disabled

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting

## License

This project is licensed under the MIT License - see the LICENSE file for details.
