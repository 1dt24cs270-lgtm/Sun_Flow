from flask import Flask, render_template, redirect, url_for, session, g, jsonify
from pymongo.errors import PyMongoError
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os

load_dotenv()

bcrypt = Bcrypt()
login_manager = LoginManager()
mongo = PyMongo()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Initialize MongoDB
    mongo.init_app(app, uri=app.config['MONGO_URI'])
    
    # Initialize extensions
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.customer_signin'
    login_manager.login_message_category = 'info'
    
    # Assign MongoDB reference to models
    from models import mongo as model_mongo
    model_mongo.db = mongo.db
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from models import Operator, Customer
        # Try operator first
        user = Operator.find_by_id(user_id)
        if user:
            return user
        # Try customer
        user = Customer.find_by_id(user_id)
        if user:
            return user
        return None

    # Context processor to inject user state globally into templates
    @app.context_processor
    def inject_user():
        user_data = None
        user_role = session.get('user_role') or session.get('user_type')
        if current_user and current_user.is_authenticated:
            if hasattr(current_user, 'to_public_dict'):
                user_data = current_user.to_public_dict()
            else:
                user_data = {
                    'id': str(getattr(current_user, '_id', '')),
                    'name': getattr(current_user, 'name', ''),
                    'email': getattr(current_user, 'email', ''),
                    'role': getattr(current_user, 'role', user_role or 'CUSTOMER')
                }
        return dict(current_user=current_user, user_profile=user_data, user_role=user_role)
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.operator import operator_bp
    from routes.customer import customer_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(operator_bp)
    app.register_blueprint(customer_bp)
    
    # Home route
    @app.route('/')
    def home():
        return render_template('base.html')
    
    # Create indexes for MongoDB
    with app.app_context():
        try:
            mongo.db.command('ping')
            mongo.db.operators.create_index('email', unique=True)
            mongo.db.customers.create_index('email', unique=True)
            mongo.db.trips.create_index('trip_id', unique=True)
            mongo.db.trips.create_index('operator_id')
            mongo.db.trips.create_index('status')
            mongo.db.bookings.create_index('booking_id', unique=True)
            mongo.db.bookings.create_index('customer_id')
            mongo.db.bookings.create_index('operator_id')
            mongo.db.bookings.create_index('trip_id')
            app.logger.info('MongoDB connected: %s', mongo.db.name)
        except PyMongoError:
            app.logger.exception('MongoDB connection failed. Check MONGO_URI and ensure MongoDB is running.')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)