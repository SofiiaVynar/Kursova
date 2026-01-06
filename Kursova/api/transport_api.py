from flask import Blueprint, request, jsonify

from services.fleet_service import FleetService
from infrastructure.repositories import (
    VehicleRepository,
    DriverRepository,
    TripRepository,
    MaintenanceRepository,
    ExpenseRepository
)

from patterns.factory import ExpenseFactory
from patterns.strategy import (
    VehicleLoadReport,
    CostReport,
    PeriodAnalyticsReport
)

service = FleetService()

vehicle_bp = Blueprint('vehicles', __name__)
driver_bp = Blueprint('drivers', __name__)
trip_bp = Blueprint('trips', __name__)
maintenance_bp = Blueprint('maintenance', __name__)
expense_bp = Blueprint('expenses', __name__)
report_bp = Blueprint('reports', __name__)


@vehicle_bp.route('/', methods=['POST'])
def create_vehicle():
    vehicle = service.add_vehicle(request.json)
    return jsonify({'id': vehicle.id}), 201


@vehicle_bp.route('/', methods=['GET'])
def get_vehicles():
    vehicles = VehicleRepository().get_all()
    return jsonify([{'id': v.id, 'brand': v.brand} for v in vehicles])


@driver_bp.route('/', methods=['POST'])
def create_driver():
    driver = service.add_driver(request.json)
    return jsonify({'id': driver.id}), 201


@trip_bp.route('/', methods=['POST'])
def create_trip():
    trip = service.add_trip(request.json)
    return jsonify({'id': trip.id}), 201


@maintenance_bp.route('/', methods=['POST'])
def create_maintenance():
    maintenance = service.plan_maintenance(request.json)
    return jsonify({'id': maintenance.id}), 201


@expense_bp.route('/', methods=['POST'])
def create_expense():
    data = request.json
    expense = ExpenseFactory.create(
        vehicle_id=data['vehicle_id'],
        expense_type=data['expense_type'],
        amount=data['amount'],
        expense_date=data['expense_date']
    )
    ExpenseRepository().add(expense)
    return jsonify({'id': expense.id}), 201


@report_bp.route('/load', methods=['GET'])
def load_report():
    trips = TripRepository().get_all()
    report = VehicleLoadReport().generate(trips)
    return jsonify(report)


@report_bp.route('/costs', methods=['GET'])
def costs_report():
    expenses = ExpenseRepository().get_all()
    report = CostReport().generate(expenses)
    return jsonify(report)


@report_bp.route('/period', methods=['GET'])
def period_report():
    start = request.args.get('start')
    end = request.args.get('end')
    trips = TripRepository().get_by_period(start, end)
    expenses = ExpenseRepository().get_by_period(start, end)
    report = PeriodAnalyticsReport().generate(trips, expenses)
    return jsonify(report)
