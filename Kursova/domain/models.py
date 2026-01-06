from flask_login import UserMixin
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db


class Vehicle(db.Model):
    __tablename__ = 'vehicles'

    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    vin = db.Column(db.String(17), unique=True, nullable=False)
    technical_status = db.Column(db.String(50), nullable=False)
    mileage = db.Column(db.Integer, default=0)
    insurance_expiry = db.Column(db.Date)


class Driver(db.Model):
    __tablename__ = 'drivers'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    license_number = db.Column(db.String(50), unique=True, nullable=False)
    experience_years = db.Column(db.Integer, nullable=False)
    medical_check_date = db.Column(db.Date, nullable=False)


# domain/models.py
class Trip(db.Model):
    __tablename__ = 'trips'

    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=False)
    trip_date = db.Column(db.Date, nullable=False)
    route = db.Column(db.String(255), nullable=False)
    distance_km = db.Column(db.Integer, nullable=False)
    fuel_cost = db.Column(db.Float, nullable=False, default=0.0)

    # Встановлюємо відношення
    driver = db.relationship('Driver', backref='trips')
    vehicle = db.relationship('Vehicle', backref='trips')


class Maintenance(db.Model):
    __tablename__ = 'maintenance'

    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    maintenance_type = db.Column(db.String(50), nullable=False)
    planned_date = db.Column(db.Date, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    cost = db.Column(db.Numeric(10, 2))

    vehicle = db.relationship('Vehicle', backref='maintenances')


class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    expense_type = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    expense_date = db.Column(db.Date, nullable=False)

    vehicle = relationship("Vehicle", backref="expenses")


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    notification_type = db.Column(db.String(50))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime)
    is_read = db.Column(db.Boolean, default=False)


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
