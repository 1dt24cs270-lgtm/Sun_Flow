from bson import ObjectId
from datetime import datetime
from models import mongo

class Trip:
    """Trip/Route model for MongoDB"""
    
    def __init__(self, data):
        self._id = data.get('_id')
        self.id = str(data.get('_id')) if data.get('_id') else None
        self.trip_id = data.get('trip_id')
        self.operator_id = str(data.get('operator_id')) if data.get('operator_id') else ''
        self.operator_name = data.get('operator_name', '')
        self.company_name = data.get('company_name', '')
        self.start_location = data.get('start_location') or data.get('start', '')
        self.end_location = data.get('end_location') or data.get('end', '')
        self.waypoints = data.get('waypoints', [])
        self.departure_time = data.get('departure_time')
        self.arrival_time = data.get('arrival_time')
        self.cargo_type = data.get('cargo_type', 'General Freight')
        self.weight = float(data.get('weight', 0.0))
        self.volume = data.get('volume', '')
        self.vehicle_type = data.get('vehicle_type', 'Dry Van')
        self.special_requirements = data.get('special_requirements', 'None')
        self.flexibility = data.get('flexibility', '')
        self.asking_rate = float(data.get('asking_rate') or data.get('rate', 0.0))
        self.capacity = int(data.get('capacity', 100))
        self.status = data.get('status', 'open')
        self.description = data.get('description', '')
        self.bookings_count = int(data.get('bookings_count', 0))
        self.total_revenue = float(data.get('total_revenue', 0.0))
        self.created_at = data.get('created_at', datetime.utcnow())
        self.updated_at = data.get('updated_at', datetime.utcnow())
    
    def to_dict(self):
        return {
            'trip_id': self.trip_id,
            'operator_id': self.operator_id,
            'operator_name': self.operator_name,
            'company_name': self.company_name,
            'start_location': self.start_location,
            'end_location': self.end_location,
            'waypoints': self.waypoints,
            'departure_time': self.departure_time,
            'arrival_time': self.arrival_time,
            'cargo_type': self.cargo_type,
            'weight': self.weight,
            'volume': self.volume,
            'vehicle_type': self.vehicle_type,
            'special_requirements': self.special_requirements,
            'flexibility': self.flexibility,
            'asking_rate': self.asking_rate,
            'capacity': self.capacity,
            'status': self.status,
            'description': self.description,
            'bookings_count': self.bookings_count,
            'total_revenue': self.total_revenue,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def to_public_dict(self):
        d = self.to_dict()
        d['_id'] = self.id
        d['id'] = self.id
        if isinstance(d.get('departure_time'), datetime):
            d['departure_time'] = d['departure_time'].isoformat()
        if isinstance(d.get('arrival_time'), datetime):
            d['arrival_time'] = d['arrival_time'].isoformat()
        if isinstance(d.get('created_at'), datetime):
            d['created_at'] = d['created_at'].isoformat()
        if isinstance(d.get('updated_at'), datetime):
            d['updated_at'] = d['updated_at'].isoformat()
        return d

    @staticmethod
    def find_by_id(trip_id):
        try:
            data = mongo.db.trips.find_one({'_id': ObjectId(trip_id)})
            if data:
                return Trip(data)
        except Exception:
            pass
        return None
    
    @staticmethod
    def find_by_trip_id(trip_id):
        data = mongo.db.trips.find_one({'trip_id': trip_id})
        if data:
            return Trip(data)
        return None
    
    @staticmethod
    def find_by_operator(operator_id):
        cursor = mongo.db.trips.find({'operator_id': str(operator_id)}).sort('created_at', -1)
        return [Trip(doc) for doc in cursor]
    
    @staticmethod
    def find_available():
        cursor = mongo.db.trips.find({'status': 'open'}).sort('created_at', -1)
        return [Trip(doc) for doc in cursor]
    
    def save(self):
        data = self.to_dict()
        if self._id:
            mongo.db.trips.update_one(
                {'_id': self._id},
                {'$set': {'updated_at': datetime.utcnow(), **data}}
            )
        else:
            result = mongo.db.trips.insert_one(data)
            self._id = result.inserted_id
            self.id = str(self._id)
        return self