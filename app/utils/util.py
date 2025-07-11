from datetime import datetime, timedelta, timezone
from jose import jwt
import jose
from functools import wraps
from flask import request, jsonify

SECRET_KEY = "a super secret, secret key"

def encode_token(customer_id): #using unique pieces of info to make our tokens user specific
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0,hours=1), #Setting the expiration time to an hour past now
        'iat': datetime.now(timezone.utc), #Issued at
        'sub':  str(customer_id) #This needs to be a string or the token will be malformed and won't be able to be decoded.
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def encode_mec_token(mechanic_id): #using unique pieces of info to make our tokens user specific
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0,hours=1), #Setting the expiration time to an hour past now
        'iat': datetime.now(timezone.utc), #Issued at
        'sub':  str(mechanic_id) #This needs to be a string or the token will be malformed and won't be able to be decoded.
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'message': 'Authorization header is missing.'}), 401
        
        if auth_header.startswith('Bearer '):
            token = auth_header.split(" ")[1]
        else:
            token = auth_header

        try:
            # Decode the token
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            customer_id = data['sub']  # Fetch the user ID
            
        except jose.exceptions.ExpiredSignatureError:
             return jsonify({'message': 'Token has expired!'}), 401
        except jose.exceptions.JWTError:
             return jsonify({'message': 'Invalid token!'}), 401

        return f(customer_id, *args, **kwargs)

    return decorated

def mec_token_required(f):
    @wraps(f)
    def mec_decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'message': 'Authorization header is missing.'}), 401
        
        if auth_header.startswith('Bearer '):
            token = auth_header.split(" ")[1]
        else:
            token = auth_header

        try:
            # Decode the token
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            mechanic_id = data['sub']  # Fetch the user ID
            
        except jose.exceptions.ExpiredSignatureError:
             return jsonify({'message': 'Token has expired!'}), 401
        except jose.exceptions.JWTError:
             return jsonify({'message': 'Invalid token!'}), 401

        return f(mechanic_id, *args, **kwargs)

    return mec_decorated