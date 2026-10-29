from bson import ObjectId
from datetime import datetime
from models import mongo

class Booking:
    """Booking model for MongoDB"""
    
    def __init__(self, data):
        self._id = data.get('_id')
        self.id = str(data.get('_id')) if data.get('_id') else None
        self.booking_id = data.get('booking_id')
        self.trip_id = str(data.get('trip_id')) if data.get('trip_id') else ''
        self.customer_id = str(data.get('customer_id')) if data.get('customer_id') else ''
        self.operator_id = str(data.get('operator_id')) if data.get('operator_id') else ''
        self.customer_name = data.get('customer_name', '')
        self.customer_phone = data.get('customer_phone', '')
        self.cargo_description = data.get('cargo_description', '')
        self.weight = float(data.get('weight', 0.0))
        self.pickup_location = data.get('pickup_location', '')
        self.dropoff_location = data.get('dropoff_location', '')
        self.amount = float(data.get('amount', 0.0))
        self.status = data.get('status', 'pending')
        self.booking_date = data.get('booking_date', datetime.utcnow())
        self.confirmed_at = data.get('confirmed_at')
        self.delivered_at = data.get('delivered_at')
        self.created_at = data.get('created_at', datetime.utcnow())
        self.updated_at = data.get('updated_at', datetime.utcnow())
    
    def to_dict(self):
        return {
            'booking_id': self.booking_id,
            'trip_id': self.trip_id,
            'customer_id': self.customer_id,
            'operator_id': self.operator_id,
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'cargo_description': self.cargo_description,
            'weight': self.weight,
            'pickup_location': self.pickup_location,
            'dropoff_location': self.dropoff_location,
            'amount': self.amount,
            'status': self.status,
            'booking_date': self.booking_date,
            'confirmed_at': self.confirmed_at,
            'delivered_at': self.delivered_at,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def to_public_dict(self):
        d = self.to_dict()
        d['_id'] = self.id
        d['id'] = self.id
        if isinstance(d.get('booking_date'), datetime):
            d['booking_date'] = d['booking_date'].isoformat()
        if isinstance(d.get('confirmed_at'), datetime):
            d['confirmed_at'] = d['confirmed_at'].isoformat()
        if isinstance(d.get('delivered_at'), datetime):
            d['delivered_at'] = d['delivered_at'].isoformat()
        if isinstance(d.get('created_at'), datetime):
            d['created_at'] = d['created_at'].isoformat()
        if isinstance(d.get('updated_at'), datetime):
            d['updated_at'] = d['updated_at'].isoformat()
        return d
    
    @staticmethod
    def find_by_id(booking_id):
        try:
            data = mongo.db.bookings.find_one({'_id': ObjectId(booking_id)})
            if data:
                return Booking(data)
        except Exception:
            pass
        return None
    
    @staticmethod
    def find_by_customer(customer_id):
        cursor = mongo.db.bookings.find({'customer_id': str(customer_id)}).sort('booking_date', -1)
        return [Booking(doc) for doc in cursor]
    
    @staticmethod
    def find_by_trip(trip_id):
        cursor = mongo.db.bookings.find({'trip_id': str(trip_id)}).sort('booking_date', -1)
        return [Booking(doc) for doc in cursor]

    @staticmethod
    def find_by_operator(operator_id):
        cursor = mongo.db.bookings.find({'operator_id': str(operator_id)}).sort('booking_date', -1)
        return [Booking(doc) for doc in cursor]
    
    def save(self):
        data = self.to_dict()
        if self._id:
            mongo.db.bookings.update_one(
                {'_id': self._id},
                {'$set': {'updated_at': datetime.utcnow(), **data}}
            )
        else:
            result = mongo.db.bookings.insert_one(data)
            self._id = result.inserted_id
            self.id = str(self._id)
        return self