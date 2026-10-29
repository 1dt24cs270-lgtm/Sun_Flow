from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from flask_login import login_required, current_user
from models import Trip, Booking, Operator, mongo
from datetime import datetime
from bson import ObjectId

operator_bp = Blueprint('operator', __name__, url_prefix='/operator')

@operator_bp.route('/dashboard')
@login_required
def dashboard():
    if session.get('user_type') != 'operator' and getattr(current_user, 'role', '') != 'OPERATOR':
        return redirect('/auth/logout')
    
    op_id = str(current_user._id)
    trips_cursor = mongo.db.trips.find({'operator_id': op_id}).sort('created_at', -1)
    trips = list(trips_cursor)
    
    for trip in trips:
        trip['_id'] = str(trip['_id'])
        if isinstance(trip.get('departure_time'), datetime):
            trip['departure_time_str'] = trip['departure_time'].strftime('%Y-%m-%d %H:%M')
        if isinstance(trip.get('arrival_time'), datetime):
            trip['arrival_time_str'] = trip['arrival_time'].strftime('%Y-%m-%d %H:%M')
    
    bookings_cursor = mongo.db.bookings.find({'operator_id': op_id}).sort('booking_date', -1)
    bookings = list(bookings_cursor)
    for b in bookings:
        b['_id'] = str(b['_id'])
    
    stats = {
        'total_trips': len(trips),
        'completed': sum(1 for t in trips if t.get('status') == 'completed'),
        'active': sum(1 for t in trips if t.get('status') in ['open', 'booked', 'in-transit']),
        'pending': sum(1 for t in trips if t.get('status') == 'pending'),
        'total_revenue': sum(t.get('total_revenue', 0.0) for t in trips)
    }
    
    return render_template('operator/dashboard.html', 
                         operator=current_user, 
                         trips=trips, 
                         bookings=bookings,
                         stats=stats)

@operator_bp.route('/route-planner')
@login_required
def route_planner():
    if session.get('user_type') != 'operator' and getattr(current_user, 'role', '') != 'OPERATOR':
        return redirect('/auth/logout')
    return render_template('operator/route_planner.html', operator=current_user)

@operator_bp.route('/analytics')
@login_required
def analytics():
    if session.get('user_type') != 'operator' and getattr(current_user, 'role', '') != 'OPERATOR':
        return redirect('/auth/logout')
    
    trips = list(mongo.db.trips.find({'operator_id': str(current_user._id)}))
    for t in trips:
        t['_id'] = str(t['_id'])
    
    revenue_data = {
        'week': [0, 0, 0, 0, 0, 0, 0],
        'month': [0] * 12,
        'year': [0] * 6
    }
    
    return render_template('operator/analytics.html', 
                         operator=current_user, 
                         trips=trips, 
                         revenue_data=revenue_data)

@operator_bp.route('/api/trips', methods=['GET', 'POST'])
@login_required
def manage_trips():
    if session.get('user_type') != 'operator' and getattr(current_user, 'role', '') != 'OPERATOR':
        return jsonify({'error': 'Unauthorized'}), 401
    
    op_id = str(current_user._id)

    if request.method == 'GET':
        trips = list(mongo.db.trips.find({'operator_id': op_id}).sort('created_at', -1))
        for trip in trips:
            trip['_id'] = str(trip['_id'])
        return jsonify(trips)
    
    # POST - Create new trip
    data = request.get_json(silent=True) or request.form.to_dict()
    
    try:
        start_loc = data.get('start') or data.get('start_location') or data.get('origin')
        end_loc = data.get('end') or data.get('end_location') or data.get('destination')
        rate = data.get('rate') or data.get('asking_rate') or 0.0

        if not start_loc or not end_loc:
            return jsonify({'success': False, 'error': 'Origin and Destination are required'}), 400

        trip_count = mongo.db.trips.count_documents({})
        trip_id = f"RTE-{datetime.now().year}-{trip_count + 1:04d}"
        
        waypoints = data.get('waypoints', [])
        if isinstance(waypoints, str):
            waypoints = [w.strip() for w in waypoints.split(',') if w.strip()]
        
        dept_time = datetime.utcnow()
        arr_time = datetime.utcnow()
        if data.get('departure'):
            try:
                dept_time = datetime.fromisoformat(data['departure'].replace('Z', ''))
            except Exception:
                pass
        if data.get('arrival'):
            try:
                arr_time = datetime.fromisoformat(data['arrival'].replace('Z', ''))
            except Exception:
                pass

        trip_data = {
            'trip_id': trip_id,
            'operator_id': op_id,
            'operator_name': current_user.name,
            'company_name': getattr(current_user, 'company_name', '') or current_user.name,
            'start_location': start_loc,
            'end_location': end_loc,
            'waypoints': waypoints,
            'departure_time': dept_time,
            'arrival_time': arr_time,
            'cargo_type': data.get('cargo_type', 'General Freight'),
            'weight': float(data.get('weight', 1.0)),
            'volume': data.get('volume', ''),
            'vehicle_type': data.get('vehicle_type', 'Dry Van'),
            'special_requirements': data.get('requirements') or data.get('special_requirements') or 'None',
            'flexibility': data.get('flexibility', ''),
            'asking_rate': float(rate),
            'capacity': int(data.get('capacity', 100)),
            'status': 'open',
            'description': data.get('description', ''),
            'bookings_count': 0,
            'total_revenue': 0.0,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = mongo.db.trips.insert_one(trip_data)
        trip_data['_id'] = str(result.inserted_id)

        # Update operator stats
        mongo.db.operators.update_one(
            {'_id': current_user._id},
            {'$inc': {'total_trips': 1}}
        )
        
        return jsonify({
            'success': True, 
            'trip_id': trip_id,
            'id': str(result.inserted_id),
            'trip': trip_data,
            'message': 'Trip published successfully'
        }), 201
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@operator_bp.route('/api/trips/<trip_id>/status', methods=['PUT'])
@login_required
def update_trip_status(trip_id):
    if session.get('user_type') != 'operator' and getattr(current_user, 'role', '') != 'OPERATOR':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json(silent=True) or request.form.to_dict()
    new_status = data.get('status')
    
    if not new_status:
        return jsonify({'success': False, 'error': 'Status required'}), 400
    
    op_id = str(current_user._id)
    query = {'$or': [{'trip_id': trip_id}, {'_id': ObjectId(trip_id) if ObjectId.is_valid(trip_id) else None}], 'operator_id': op_id}
    
    result = mongo.db.trips.update_one(
        query,
        {'$set': {'status': new_status, 'updated_at': datetime.utcnow()}}
    )
    
    if result.modified_count > 0:
        return jsonify({'success': True, 'message': f'Trip status updated to {new_status}'})
    else:
        return jsonify({'success': False, 'error': 'Trip not found or unauthorized'}), 404

@operator_bp.route('/api/profile', methods=['PUT'])
@login_required
def update_operator_profile():
    if session.get('user_type') != 'operator' and getattr(current_user, 'role', '') != 'OPERATOR':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json(silent=True) or request.form.to_dict()
    update_fields = {}
    for field in ['name', 'phone', 'company_name', 'address', 'gstin_or_license', 'base_hub']:
        if field in data:
            update_fields[field] = data[field]
    if 'fleet_size' in data:
        update_fields['fleet_size'] = int(data['fleet_size'])
    
    update_fields['updated_at'] = datetime.utcnow()
    
    mongo.db.operators.update_one(
        {'_id': current_user._id},
        {'$set': update_fields}
    )
    
    updated_user = mongo.db.operators.find_one({'_id': current_user._id})
    updated_user['_id'] = str(updated_user['_id'])
    
    return jsonify({'success': True, 'message': 'Profile updated successfully', 'user': updated_user})