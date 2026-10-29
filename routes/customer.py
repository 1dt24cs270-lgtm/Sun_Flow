from flask import Blueprint, render_template, request, jsonify, session, redirect
from flask_login import login_required, current_user
from models import Trip, Booking, Customer, mongo
from datetime import datetime
from bson import ObjectId

customer_bp = Blueprint('customer', __name__, url_prefix='/customer')

@customer_bp.route('/dashboard')
@login_required
def dashboard():
    if session.get('user_type') != 'customer' and getattr(current_user, 'role', '') != 'CUSTOMER':
        return redirect('/auth/logout')
    
    cust_id = str(current_user._id)
    
    bookings = list(mongo.db.bookings.find({'customer_id': cust_id}).sort('booking_date', -1))
    for booking in bookings:
        booking['_id'] = str(booking['_id'])
        if booking.get('trip_id'):
            trip_doc = None
            if ObjectId.is_valid(booking['trip_id']):
                trip_doc = mongo.db.trips.find_one({'_id': ObjectId(booking['trip_id'])})
            if not trip_doc:
                trip_doc = mongo.db.trips.find_one({'trip_id': booking['trip_id']})
            if trip_doc:
                booking['trip'] = {
                    'trip_id': trip_doc.get('trip_id'),
                    'start_location': trip_doc.get('start_location'),
                    'end_location': trip_doc.get('end_location'),
                    'asking_rate': trip_doc.get('asking_rate'),
                    'vehicle_type': trip_doc.get('vehicle_type'),
                    'company_name': trip_doc.get('company_name', 'Transport Operator')
                }

    available_trips = list(mongo.db.trips.find({'status': 'open'}).sort('created_at', -1).limit(10))
    for trip in available_trips:
        trip['_id'] = str(trip['_id'])
        if isinstance(trip.get('departure_time'), datetime):
            trip['departure_time_str'] = trip['departure_time'].strftime('%Y-%m-%d %H:%M')
        if isinstance(trip.get('arrival_time'), datetime):
            trip['arrival_time_str'] = trip['arrival_time'].strftime('%Y-%m-%d %H:%M')

    stats = {
        'total_bookings': len(bookings),
        'active': sum(1 for b in bookings if b.get('status') in ['pending', 'confirmed', 'in-transit']),
        'completed': sum(1 for b in bookings if b.get('status') in ['delivered', 'completed']),
        'cancelled': sum(1 for b in bookings if b.get('status') == 'cancelled')
    }
    
    return render_template('customers/dashboard.html', 
                         customer=current_user, 
                         bookings=bookings, 
                         available_trips=available_trips,
                         stats=stats)

@customer_bp.route('/profile')
@login_required
def profile():
    if session.get('user_type') != 'customer' and getattr(current_user, 'role', '') != 'CUSTOMER':
        return redirect('/auth/logout')
    return render_template('customers/profile.html', customer=current_user)

@customer_bp.route('/shipments')
@login_required
def shipments():
    if session.get('user_type') != 'customer' and getattr(current_user, 'role', '') != 'CUSTOMER':
        return redirect('/auth/logout')
    
    cust_id = str(current_user._id)
    bookings = list(mongo.db.bookings.find({'customer_id': cust_id}).sort('booking_date', -1))
    
    for booking in bookings:
        booking['_id'] = str(booking['_id'])
        if booking.get('trip_id'):
            trip_doc = None
            if ObjectId.is_valid(booking['trip_id']):
                trip_doc = mongo.db.trips.find_one({'_id': ObjectId(booking['trip_id'])})
            if not trip_doc:
                trip_doc = mongo.db.trips.find_one({'trip_id': booking['trip_id']})
            if trip_doc:
                booking['trip'] = {
                    'trip_id': trip_doc.get('trip_id'),
                    'start': trip_doc.get('start_location'),
                    'end': trip_doc.get('end_location'),
                    'company_name': trip_doc.get('company_name', 'Carrier')
                }
    
    return render_template('customers/shipments.html', customer=current_user, bookings=bookings)

@customer_bp.route('/api/book', methods=['POST'])
@login_required
def book_trip():
    if session.get('user_type') != 'customer' and getattr(current_user, 'role', '') != 'CUSTOMER':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json(silent=True) or request.form.to_dict()
    trip_identifier = data.get('trip_id') or data.get('id')
    
    if not trip_identifier:
        return jsonify({'success': False, 'error': 'Trip identifier is required'}), 400

    # Search trip by trip_id string or ObjectId
    trip = mongo.db.trips.find_one({'trip_id': trip_identifier})
    if not trip and ObjectId.is_valid(trip_identifier):
        trip = mongo.db.trips.find_one({'_id': ObjectId(trip_identifier)})

    if not trip:
        return jsonify({'success': False, 'error': 'Trip not found'}), 404
    
    if trip.get('status') != 'open':
        return jsonify({'success': False, 'error': 'Trip is not available for booking'}), 400
    
    try:
        booking_count = mongo.db.bookings.count_documents({})
        booking_id = f"BK-{datetime.now().year}-{booking_count + 1:04d}"
        
        booking_data = {
            'booking_id': booking_id,
            'trip_id': str(trip['_id']),
            'customer_id': str(current_user._id),
            'operator_id': str(trip.get('operator_id', '')),
            'customer_name': current_user.name,
            'customer_phone': getattr(current_user, 'phone', ''),
            'cargo_description': data.get('description') or data.get('cargo_description') or 'General Freight',
            'weight': float(data.get('weight', trip.get('weight', 1.0))),
            'pickup_location': data.get('pickup') or data.get('pickup_location') or trip.get('start_location'),
            'dropoff_location': data.get('dropoff') or data.get('dropoff_location') or trip.get('end_location'),
            'amount': float(data.get('amount', trip.get('asking_rate', 0.0))),
            'status': 'pending',
            'booking_date': datetime.utcnow(),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = mongo.db.bookings.insert_one(booking_data)
        booking_data['_id'] = str(result.inserted_id)

        # Update trip booking count & revenue
        mongo.db.trips.update_one(
            {'_id': trip['_id']},
            {
                '$inc': {
                    'bookings_count': 1,
                    'total_revenue': float(booking_data['amount'])
                }
            }
        )
        
        # Update customer total bookings
        mongo.db.customers.update_one(
            {'_id': current_user._id},
            {'$inc': {'total_bookings': 1}}
        )

        # Update operator total revenue
        if trip.get('operator_id') and ObjectId.is_valid(trip['operator_id']):
            mongo.db.operators.update_one(
                {'_id': ObjectId(trip['operator_id'])},
                {'$inc': {'total_revenue': float(booking_data['amount'])}}
            )
        
        return jsonify({
            'success': True, 
            'booking_id': booking_id,
            'id': str(result.inserted_id),
            'booking': booking_data,
            'message': 'Booking confirmed!'
        }), 201
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@customer_bp.route('/api/bookings', methods=['GET'])
@login_required
def get_bookings():
    if session.get('user_type') != 'customer' and getattr(current_user, 'role', '') != 'CUSTOMER':
        return jsonify({'error': 'Unauthorized'}), 401
    
    bookings = list(mongo.db.bookings.find({'customer_id': str(current_user._id)}).sort('booking_date', -1))
    for booking in bookings:
        booking['_id'] = str(booking['_id'])
    return jsonify(bookings)

@customer_bp.route('/api/profile', methods=['PUT'])
@login_required
def update_customer_profile():
    if session.get('user_type') != 'customer' and getattr(current_user, 'role', '') != 'CUSTOMER':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json(silent=True) or request.form.to_dict()
    update_fields = {}
    for field in ['name', 'phone', 'address', 'company_name', 'gst_number']:
        if field in data:
            update_fields[field] = data[field]
    
    update_fields['updated_at'] = datetime.utcnow()
    
    mongo.db.customers.update_one(
        {'_id': current_user._id},
        {'$set': update_fields}
    )
    
    updated_user = mongo.db.customers.find_one({'_id': current_user._id})
    updated_user['_id'] = str(updated_user['_id'])
    
    return jsonify({'success': True, 'message': 'Profile updated successfully', 'user': updated_user})