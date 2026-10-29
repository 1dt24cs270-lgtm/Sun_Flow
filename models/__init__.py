from flask_pymongo import PyMongo
from bson import ObjectId
from datetime import datetime

# Initialize PyMongo
mongo = PyMongo()

# Helper to convert MongoDB documents to dict with string IDs
def serialize_doc(doc):
    if doc and '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc

def serialize_list(docs):
    return [serialize_doc(doc) for doc in docs]

# Import models for easy access
from .user import Operator, Customer
from .trip import Trip
from .booking import Booking