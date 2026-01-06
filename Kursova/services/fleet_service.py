from datetime import datetime

from domain.models import Vehicle, Driver, Trip, Maintenance, Expense
from extensions import db
from infrastructure.repositories import (
    VehicleRepository,
    DriverRepository,
    TripRepository,
    MaintenanceRepository, ExpenseRepository
)
from patterns.observer import Subject, NotificationObserver


class FleetService:
    def __init__(self):
        self.vehicles = VehicleRepository()
        self.drivers = DriverRepository()
        self.trips = TripRepository()
        self.maintenance = MaintenanceRepository()
        self.notifier = Subject()
        self.notifier.attach(NotificationObserver())

    def add_vehicle(self, data):
        v = Vehicle(**data)
        self.vehicles.add(v)
        self.notifier.notify("Vehicle registered")
        return v

    def add_driver(self, data):
        d = Driver(**data)
        self.drivers.add(d)
        return d

    def add_trip(self, data):
        t = Trip(**data)
        self.trips.add(t)
        return t

    def plan_maintenance(self, data):
        m = Maintenance(**data)
        self.maintenance.add(m)
        self.notifier.notify("Maintenance planned")
        return m

    def add_trip(self, data):
        distance = int(data['distance_km'])
        fuel_amount = float(data['fuel_cost'])  # беремо лише введене

        trip = Trip(
            vehicle_id=int(data['vehicle_id']),
            driver_id=int(data['driver_id']),
            trip_date=datetime.strptime(data['trip_date'], '%Y-%m-%d').date(),
            route=data['route'],
            distance_km=distance,
            fuel_cost=fuel_amount
        )

        db.session.add(trip)
        db.session.commit()

        # додаємо витрату на пальне
        ExpenseRepository().add(
            vehicle_id=trip.vehicle_id,
            expense_type="Пальне",
            amount=fuel_amount,
            expense_date=trip.trip_date
        )

        return trip

    @staticmethod
    def get_all_trips():
        return TripRepository.get_all()

    @staticmethod
    def get_vehicle_load():
        vehicles = VehicleRepository().get_all()
        trips = TripRepository.get_all()
        load = {}
        for v in vehicles:
            load[v.brand + " (" + str(v.id) + ")"] = len([t for t in trips if t.vehicle_id == v.id])
        return load

    @staticmethod
    def get_other_expenses():
        expenses = ExpenseRepository().get_all()
        result = {}
        for exp in expenses:
            if exp.expense_type != "Пальне":
                result[exp.expense_type] = result.get(exp.expense_type, 0) + exp.amount
        return result

    @staticmethod
    def get_trips_by_period(start, end):
        trips = TripRepository.get_all()
        start_date = datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.strptime(end, "%Y-%m-%d").date()
        return [t for t in trips if start_date <= t.trip_date <= end_date]

    def add_maintenance(self, data):
        from datetime import datetime

        maintenance = Maintenance(
            vehicle_id=int(data['vehicle_id']),
            maintenance_type=data['maintenance_type'],
            planned_date=datetime.strptime(data['planned_date'], '%Y-%m-%d').date(),
            cost=float(data['cost']),
            completed=False
        )

        db.session.add(maintenance)
        expense = Expense(
            vehicle_id=maintenance.vehicle_id,
            expense_type=f"ТО: {maintenance.maintenance_type}",
            amount=maintenance.cost,
            expense_date=maintenance.planned_date
        )
        db.session.add(expense)
        db.session.commit()

        return maintenance