from datetime import datetime

from extensions import db
from domain.models import Vehicle, Driver, Trip, Maintenance, Expense, db


# ----------------- VEHICLE REPOSITORY -----------------
class VehicleRepository:
    def add(self, obj):
        db.session.add(obj)
        db.session.commit()

    def get_all(self):
        return Vehicle.query.all()

    @staticmethod
    def get_by_id(vehicle_id):
        return Vehicle.query.get(vehicle_id)

    @staticmethod
    def update(vehicle_id, brand, year, vin, technical_status, mileage, insurance_expiry):
        vehicle = Vehicle.query.get(vehicle_id)
        if vehicle:
            vehicle.brand = brand
            vehicle.year = year
            vehicle.vin = vin
            vehicle.technical_status = technical_status
            vehicle.mileage = mileage
            vehicle.insurance_expiry = insurance_expiry
            db.session.commit()
        return vehicle

    @staticmethod
    def delete(vehicle_id):
        vehicle = Vehicle.query.get(vehicle_id)
        if vehicle:
            db.session.delete(vehicle)
            db.session.commit()


# ----------------- DRIVER REPOSITORY -----------------
class DriverRepository:
    def add(self, obj):
        db.session.add(obj)
        db.session.commit()

    @staticmethod
    def get_all():
        from domain.models import Driver
        return Driver.query.all()

    @staticmethod
    def get_by_id(driver_id):
        return Driver.query.get(driver_id)

    @staticmethod
    def update(driver_id, full_name, license_number, experience_years, medical_check_date):
        driver = Driver.query.get(driver_id)
        if driver:
            driver.full_name = full_name
            driver.license_number = license_number
            driver.experience_years = experience_years
            driver.medical_check_date = medical_check_date
            db.session.commit()
        return driver

    @staticmethod
    def delete(driver_id):
        driver = Driver.query.get(driver_id)
        if driver:
            db.session.delete(driver)
            db.session.commit()


class TripRepository:
    @staticmethod
    def add(obj):
        db.session.add(obj)
        db.session.commit()

        # Додаємо витрату на пальне тільки якщо fuel_cost задано
        if obj.fuel_cost and obj.vehicle_id:
            expense = Expense(
                vehicle_id=obj.vehicle_id,
                expense_type="Пальне",
                amount=obj.fuel_cost,
                expense_date=obj.trip_date
            )
            db.session.add(expense)
            db.session.commit()
        return obj

    @staticmethod
    def get_trips_by_period(start, end):
        start_date = datetime.strptime(start, '%Y-%m-%d').date()
        end_date = datetime.strptime(end, '%Y-%m-%d').date()

        return Trip.query.filter(
            Trip.trip_date.between(start_date, end_date)
        ).all()

    @staticmethod
    def get_all():
        return Trip.query.all()

    @staticmethod
    def delete_by_driver(driver_id):
        trips = Trip.query.filter_by(driver_id=driver_id).all()
        for trip in trips:
            TripRepository.delete(trip.id)

    @staticmethod
    def get_by_id(trip_id):
        return Trip.query.get(trip_id)

    @staticmethod
    def update(trip_id, vehicle_id, driver_id, trip_date, route, distance_km, fuel_cost):
        trip = Trip.query.get(trip_id)
        if trip:
            trip.vehicle_id = vehicle_id
            trip.driver_id = driver_id
            trip.trip_date = trip_date
            trip.route = route
            trip.distance_km = distance_km
            trip.fuel_cost = fuel_cost

            # Оновлюємо відповідну витрату на пальне
            expense = Expense.query.filter_by(
                vehicle_id=vehicle_id,
                expense_type="Пальне",
                expense_date=trip_date
            ).first()
            if expense:
                expense.amount = fuel_cost
            else:
                expense = Expense(
                    vehicle_id=vehicle_id,
                    expense_type="Пальне",
                    amount=fuel_cost,
                    expense_date=trip_date
                )
                db.session.add(expense)

            db.session.commit()
        return trip

    @staticmethod
    def delete(trip_id):
        trip = Trip.query.get(trip_id)
        if trip:
            # Видаляємо пов'язану витрату на пальне
            expense = Expense.query.filter_by(
                vehicle_id=trip.vehicle_id,
                expense_type="Пальне",
                expense_date=trip.trip_date
            ).first()
            if expense:
                db.session.delete(expense)
            db.session.delete(trip)
            db.session.commit()


class MaintenanceRepository:
    def __init__(self):
        self.model = Maintenance
        self.db = db

    def get_all(self):
        return self.model.query.all()

    @staticmethod
    def get_due():
        from datetime import date
        return Maintenance.query.filter(
            (Maintenance.completed == False) |
            (Maintenance.planned_date <= date.today())
        ).all()

    @staticmethod
    def delete_by_vehicle(vehicle_id):
        Maintenance.query.filter_by(vehicle_id=vehicle_id).delete()
        db.session.commit()

    def add(self, data):
        maintenance = self.model(
            vehicle_id=int(data['vehicle_id']),
            maintenance_type=data['maintenance_type'],
            planned_date=datetime.strptime(data['planned_date'], '%Y-%m-%d').date(),
            completed=False,
            cost=float(data.get('cost') or 0)
        )

        self.db.session.add(maintenance)
        self.db.session.commit()

        if maintenance.cost > 0:
            expense = Expense(
                vehicle_id=maintenance.vehicle_id,
                expense_type=f"ТО: {maintenance.maintenance_type}",
                amount=maintenance.cost,
                expense_date=maintenance.planned_date
            )
            self.db.session.add(expense)
            self.db.session.commit()

        return maintenance

    @staticmethod
    def get_by_id(maintenance_id):
        return Maintenance.query.get(maintenance_id)

    @staticmethod
    def update(maintenance_id, vehicle_id, planned_date, maintenance_type, cost):
        maintenance = Maintenance.query.get(maintenance_id)
        if not maintenance:
            return None

        maintenance.vehicle_id = vehicle_id
        maintenance.planned_date = planned_date
        maintenance.maintenance_type = maintenance_type
        maintenance.cost = cost

        # 🔄 оновлюємо витрату
        expense = Expense.query.filter_by(
            vehicle_id=vehicle_id,
            expense_type=f"ТО: {maintenance_type}",
            expense_date=planned_date
        ).first()

        if expense:
            expense.amount = cost
        else:
            expense = Expense(
                vehicle_id=vehicle_id,
                expense_type=f"ТО: {maintenance_type}",
                amount=cost,
                expense_date=planned_date
            )
            db.session.add(expense)

        db.session.commit()
        return maintenance

    @staticmethod
    def delete(maintenance_id):
        maintenance = Maintenance.query.get(maintenance_id)
        if maintenance:
            db.session.delete(maintenance)
            db.session.commit()


class ExpenseRepository:

    def add(self, vehicle_id, expense_type, amount, expense_date):
        expense = Expense(
            vehicle_id=vehicle_id,
            expense_type=expense_type,
            amount=amount,
            expense_date=expense_date
        )
        db.session.add(expense),
        db.session.commit()
        return expense

    @staticmethod
    def delete_by_vehicle(vehicle_id):
        Expense.query.filter_by(vehicle_id=vehicle_id).delete()
        db.session.commit()

    def get_all(self):
        return Expense.query.all()

    def get_by_period(self, start, end):
        return Expense.query.filter(
            Expense.expense_date.between(start, end)
        ).all()
