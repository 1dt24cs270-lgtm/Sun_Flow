from bson import ObjectId
from datetime import datetime
from flask_login import UserMixin
from models import mongo, serialize_doc

class Operator(UserMixin):
    """Operator model for MongoDB"""
    
    def __init__(self, data):
        self._id = data.get('_id')
        self.id = str(data.get('_id')) if data.get('_id') else None
        self.role = 'OPERATOR'
        self.name = data.get('name', '')
        self.email = data.get('email', '')
        self.phone = data.get('phone', '')
        self.company_name = data.get('company_name') or data.get('company') or self.name
        self.address = data.get('address', '')
        self.gstin_or_license = data.get('gstin_or_license', '')
        self.base_hub = data.get('base_hub', '')
        self.fleet_size = data.get('fleet_size', 1)
        self.password_hash = data.get('password_hash', '')
        self.truck_types = data.get('truck_types', [])
        self.verified = data.get('verified', False)
        self.rating = data.get('rating', 0.0)
        self.total_trips = data.get('total_trips', 0)
        self.total_revenue = data.get('total_revenue', 0.0)
        self.created_at = data.get('created_at', datetime.utcnow())
        self.updated_at = data.get('updated_at', datetime.utcnow())
    
    def to_dict(self):
        return {
            'role': 'OPERATOR',
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'company_name': self.company_name,
            'address': self.address,
            'gstin_or_license': self.gstin_or_license,
            'base_hub': self.base_hub,
            'fleet_size': self.fleet_size,
            'password_hash': self.password_hash,
            'truck_types': self.truck_types,
            'verified': self.verified,
            'rating': self.rating,
            'total_trips': self.total_trips,
            'total_revenue': self.total_revenue,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def to_public_dict(self):
        return {
            'id': self.id,
            '_id': self.id,
            'role': 'OPERATOR',
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'company_name': self.company_name,
            'address': self.address,
            'gstin_or_license': self.gstin_or_license,
            'base_hub': self.base_hub,
            'fleet_size': self.fleet_size,
            'truck_types': self.truck_types,
            'verified': self.verified,
            'rating': self.rating,
            'total_trips': self.total_trips,
            'total_revenue': self.total_revenue
        }
    
    def get_id(self):
        return str(self._id) if self._id else None
    
    @staticmethod
    def find_by_email(email):
        if not email:
            return None
        data = mongo.db.operators.find_one({'email': email.lower().strip()})
        if data:
            return Operator(data)
        return None
    
    @staticmethod
    def find_by_id(user_id):
        try:
            data = mongo.db.operators.find_one({'_id': ObjectId(user_id)})
            if data:
                return Operator(data)
        except Exception:
            pass
        return None
    
    def save(self):
        data = self.to_dict()
        if self._id:
            mongo.db.operators.update_one(
                {'_id': self._id},
                {'$set': {'updated_at': datetime.utcnow(), **data}}
            )
        else:
            result = mongo.db.operators.insert_one(data)
            self._id = result.inserted_id
            self.id = str(self._id)
        return self


class Customer(UserMixin):
    """Customer model for MongoDB"""
    
    def __init__(self, data):
        self._id = data.get('_id')
        self.id = str(data.get('_id')) if data.get('_id') else None
        self.role = 'CUSTOMER'
        self.name = data.get('name', '')
        self.email = data.get('email', '')
        self.phone = data.get('phone', '')
        self.address = data.get('address', '')
        self.company_name = data.get('company_name') or data.get('company') or ''
        self.gst_number = data.get('gst_number', '')
        self.password_hash = data.get('password_hash', '')
        self.verified = data.get('verified', False)
        self.rating = data.get('rating', 0.0)
        self.total_bookings = data.get('total_bookings', 0)
        self.created_at = data.get('created_at', datetime.utcnow())
        self.updated_at = data.get('updated_at', datetime.utcnow())
    
    def to_dict(self):
        return {
            'role': 'CUSTOMER',
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'company_name': self.company_name,
            'gst_number': self.gst_number,
            'password_hash': self.password_hash,
            'verified': self.verified,
            'rating': self.rating,
            'total_bookings': self.total_bookings,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def to_public_dict(self):
        return {
            'id': self.id,
            '_id': self.id,
            'role': 'CUSTOMER',
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'company_name': self.company_name,
            'gst_number': self.gst_number,
            'verified': self.verified,
            'rating': self.rating,
            'total_bookings': self.total_bookings
        }
    
    def get_id(self):
        return str(self._id) if self._id else None
    
    @staticmethod
    def find_by_email(email):
        if not email:
            return None
        data = mongo.db.customers.find_one({'email': email.lower().strip()})
        if data:
            return Customer(data)
        return None
    
    @staticmethod
    def find_by_id(user_id):
        try:
            data = mongo.db.customers.find_one({'_id': ObjectId(user_id)})
            if data:
                return Customer(data)
        except Exception:
            pass
        return None
    
    def save(self):
        data = self.to_dict()
        if self._id:
            mongo.db.customers.update_one(
                {'_id': self._id},
                {'$set': {'updated_at': datetime.utcnow(), **data}}
            )
        else:
            result = mongo.db.customers.insert_one(data)
            self._id = result.inserted_id
            self.id = str(self._id)
        return self