from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from models import Operator, Customer, mongo
from datetime import datetime
from pymongo.errors import DuplicateKeyError
import re

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

def is_valid_email(email):
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email.strip()) is not None

# Unified API endpoints
@auth_bp.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.get_json(silent=True) or request.form.to_dict()
    role = (data.get('role') or data.get('user_type') or 'CUSTOMER').upper()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password')
    name = (data.get('name') or data.get('full_name') or '').strip()
    phone = (data.get('phone') or '').strip()

    if not email or not password or not name:
        return jsonify({'success': False, 'error': 'Name, email, and password are required'}), 400

    if not is_valid_email(email):
        return jsonify({'success': False, 'error': 'Invalid email format'}), 400

    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    try:
        if role == 'OPERATOR':
            if Operator.find_by_email(email):
                return jsonify({'success': False, 'error': 'Email already registered'}), 400

            company = data.get('company_name') or data.get('company') or name
            truck_types = data.get('truck_types', [])
            if isinstance(truck_types, str):
                truck_types = [t.strip() for t in truck_types.split(',') if t.strip()]

            operator_data = {
                'name': name,
                'email': email,
                'phone': phone,
                'company_name': company,
                'address': data.get('address', ''),
                'gstin_or_license': data.get('gstin_or_license') or data.get('license', ''),
                'base_hub': data.get('base_hub') or data.get('hub', ''),
                'fleet_size': int(data.get('fleet_size', 1)),
                'password_hash': password_hash,
                'truck_types': truck_types,
                'verified': False,
                'rating': 0.0,
                'total_trips': 0,
                'total_revenue': 0.0,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            op = Operator(operator_data).save()
            login_user(op)
            session['user_type'] = 'operator'
            session['user_role'] = 'OPERATOR'
            session['user_id'] = op.id

            return jsonify({
                'success': True,
                'message': 'Operator registered successfully',
                'redirect': '/operator/dashboard',
                'user': op.to_public_dict()
            }), 201

        else:
            # CUSTOMER
            if Customer.find_by_email(email):
                return jsonify({'success': False, 'error': 'Email already registered'}), 400

            customer_data = {
                'name': name,
                'email': email,
                'phone': phone,
                'address': data.get('address', ''),
                'company_name': data.get('company_name') or data.get('company', ''),
                'gst_number': data.get('gst_number') or data.get('gst', ''),
                'password_hash': password_hash,
                'verified': False,
                'rating': 0.0,
                'total_bookings': 0,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            cust = Customer(customer_data).save()
            login_user(cust)
            session['user_type'] = 'customer'
            session['user_role'] = 'CUSTOMER'
            session['user_id'] = cust.id

            return jsonify({
                'success': True,
                'message': 'Customer registered successfully',
                'redirect': '/customer/dashboard',
                'user': cust.to_public_dict()
            }), 201

    except DuplicateKeyError:
        return jsonify({'success': False, 'error': 'Email already registered'}), 409
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@auth_bp.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json(silent=True) or request.form.to_dict()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password')
    requested_role = (data.get('role') or data.get('user_type') or '').upper()

    if not email or not password:
        return jsonify({'success': False, 'error': 'Email and password required'}), 400

    # Try operator if requested or as fallback
    user = None
    role = None

    if requested_role == 'OPERATOR':
        op = Operator.find_by_email(email)
        if op and bcrypt.check_password_hash(op.password_hash, password):
            user = op
            role = 'OPERATOR'
    elif requested_role == 'CUSTOMER':
        cust = Customer.find_by_email(email)
        if cust and bcrypt.check_password_hash(cust.password_hash, password):
            user = cust
            role = 'CUSTOMER'
    else:
        # Search operator first, then customer
        op = Operator.find_by_email(email)
        if op and bcrypt.check_password_hash(op.password_hash, password):
            user = op
            role = 'OPERATOR'
        else:
            cust = Customer.find_by_email(email)
            if cust and bcrypt.check_password_hash(cust.password_hash, password):
                user = cust
                role = 'CUSTOMER'

    if not user:
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

    login_user(user, remember=data.get('remember_me', False))
    session['user_type'] = role.lower()
    session['user_role'] = role
    session['user_id'] = user.id

    redirect_url = '/operator/dashboard' if role == 'OPERATOR' else '/customer/dashboard'

    return jsonify({
        'success': True,
        'message': 'Login successful!',
        'redirect': redirect_url,
        'user': user.to_public_dict()
    })


@auth_bp.route('/api/auth/me', methods=['GET'])
def api_me():
    if current_user and current_user.is_authenticated:
        role = session.get('user_role') or ('OPERATOR' if getattr(current_user, 'role', None) == 'OPERATOR' else 'CUSTOMER')
        return jsonify({
            'authenticated': True,
            'user': current_user.to_public_dict() if hasattr(current_user, 'to_public_dict') else {
                'id': str(current_user._id),
                'name': getattr(current_user, 'name', ''),
                'email': getattr(current_user, 'email', ''),
                'role': role
            }
        })
    return jsonify({'authenticated': False, 'user': None}), 401


@auth_bp.route('/api/auth/logout', methods=['GET', 'POST'])
def api_logout():
    logout_user()
    session.clear()
    if request.is_json or request.path.startswith('/api/'):
        return jsonify({'success': True, 'message': 'Logged out successfully', 'redirect': '/'})
    return redirect(url_for('home'))


# Form rendering & traditional auth routes for compatibility
@auth_bp.route('/auth/operator/signup', methods=['GET', 'POST'])
def operator_signup():
    if request.method == 'GET':
        return render_template('auth/tranport_operator_Sign_page_register.html')
    data = request.get_json(silent=True) or request.form.to_dict()
    data['role'] = 'OPERATOR'
    request.get_json = lambda **kw: data
    return api_register()


@auth_bp.route('/auth/operator/signin', methods=['GET', 'POST'])
def operator_signin():
    if request.method == 'GET':
        return render_template('auth/tranport_operator_Sign_page_register.html')
    data = request.get_json(silent=True) or request.form.to_dict()
    data['role'] = 'OPERATOR'
    request.get_json = lambda **kw: data
    return api_login()


@auth_bp.route('/auth/customer/signup', methods=['GET', 'POST'])
def customer_signup():
    if request.method == 'GET':
        return render_template('auth/customer_signin_register.html')
    data = request.get_json(silent=True) or request.form.to_dict()
    data['role'] = 'CUSTOMER'
    request.get_json = lambda **kw: data
    return api_register()


@auth_bp.route('/auth/customer/signin', methods=['GET', 'POST'])
def customer_signin():
    if request.method == 'GET':
        return render_template('auth/customer_signin_register.html')
    data = request.get_json(silent=True) or request.form.to_dict()
    data['role'] = 'CUSTOMER'
    request.get_json = lambda **kw: data
    return api_login()


@auth_bp.route('/auth/logout')
def logout():
    return api_logout()