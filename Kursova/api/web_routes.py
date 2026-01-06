from _pydecimal import Decimal
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, logout_user, login_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from api.transport_api import maintenance_bp
from domain.models import User, Maintenance, Trip, Expense, Notification
from extensions import db
from infrastructure.repositories import VehicleRepository, DriverRepository, TripRepository, MaintenanceRepository, \
    ExpenseRepository
from patterns.strategy import VehicleLoadReport, CostReport, PeriodAnalyticsReport
from services.fleet_service import FleetService
from services.notification_service import NotificationService

web_bp = Blueprint('web', __name__)
auth_bp = Blueprint('auth', __name__)
service = FleetService()


@web_bp.before_request
def run_notifications():
    if not current_user.is_authenticated:
        return

    # Відключаємо для логіну та реєстрації
    if request.endpoint in ['auth.login', 'auth.register', 'auth.logout']:
        return

    # Або для всіх ендпоінтів auth
    if request.endpoint and request.endpoint.startswith('auth.'):
        return

    notifications = NotificationService.get_all_notifications()
    for note in notifications:
        flash(note, 'warning')


# ----------------- HOME -----------------
@web_bp.route('/')
def home():
    return render_template('home.html')


# ----------------- VEHICLES -----------------
@web_bp.route('/vehicles', methods=['GET', 'POST'])
def vehicles_page():
    vehicles = VehicleRepository().get_all()  # перегляд доступний усім
    if request.method == 'POST':
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash("Доступ заборонено!", "danger")
            return redirect(url_for('web.vehicles_page'))
        service.add_vehicle(request.form)
        return redirect(url_for('web.vehicles_page'))
    return render_template('vehicles.html', vehicles=vehicles)


@web_bp.route('/drivers', methods=['GET', 'POST'])
def drivers_page():
    drivers = DriverRepository().get_all()

    # Обробка додавання нового водія
    if request.method == 'POST':
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash("Доступ заборонено!", "danger")
            return redirect(url_for('web.drivers_page'))

        # Використовуємо сервіс для додавання водія
        service.add_driver(request.form)
        flash("Водія додано успішно!", "success")
        return redirect(url_for('web.drivers_page'))

    # GET запит — просто показуємо сторінку
    return render_template('drivers.html', drivers=drivers)


@web_bp.route('/trips', methods=['GET', 'POST'])
def trips_page():
    trips = TripRepository().get_all()
    drivers = DriverRepository().get_all()
    vehicles = VehicleRepository().get_all()

    if request.method == 'POST':
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash("Доступ заборонено!", "danger")
            return redirect(url_for('web.trips_page'))

        trip_data = request.form
        trip = Trip(
            vehicle_id=int(trip_data['vehicle_id']),
            driver_id=int(trip_data['driver_id']),
            trip_date=datetime.strptime(trip_data['trip_date'], '%Y-%m-%d').date(),
            route=trip_data['route'],
            distance_km=float(trip_data['distance_km']),
            fuel_cost=float(trip_data['fuel_cost'])
        )
        TripRepository.add(trip)

        flash("Поїздка додана разом із витратою на пальне", "success")
        return redirect(url_for('web.trips_page'))

    return render_template('trips.html', trips=trips, drivers=drivers, vehicles=vehicles)


@web_bp.route('/maintenance', methods=['GET', 'POST'])
def maintenance_page():
    maintenances = MaintenanceRepository().get_all()
    vehicles = VehicleRepository().get_all()

    if request.method == 'POST':
        if not current_user.is_authenticated:  # тепер всі увійшлі користувачі
            flash("Доступ заборонено!", "danger")
            return redirect(url_for('web.maintenance_page'))

        service.add_maintenance(request.form)
        flash("ТО додано успішно!", "success")
        return redirect(url_for('web.maintenance_page'))

    # Передаємо змінну admin у шаблон
    admin = current_user.is_authenticated
    return render_template('maintenance.html', maintenances=maintenances, vehicles=vehicles, admin=admin)


@web_bp.route('/expenses')
def expenses_page():
    expenses = ExpenseRepository().get_all()
    return render_template('expenses.html', expenses=expenses)


@web_bp.route('/reports')
@login_required
def reports_page():
    all_trips = TripRepository.get_all()
    all_expenses = ExpenseRepository().get_all()

    # Пальне
    fuel_cost = sum(
        (Decimal(str(t.distance_km)) * Decimal(str(t.fuel_cost)))
        for t in all_trips if t.fuel_cost
    )

    # ТО
    maintenance_cost = sum(
        Decimal(str(e.amount)) for e in all_expenses if 'ТО' in e.expense_type
    )

    # Інші витрати (крім ТО та пального)
    other_expenses = {}
    for e in all_expenses:
        if 'ТО' not in e.expense_type and 'Пальне' not in e.expense_type:
            other_expenses[e.expense_type] = other_expenses.get(e.expense_type, Decimal('0')) + Decimal(str(e.amount))

    # Формуємо звіт
    cost_report = {
        'Пальне': fuel_cost,
        'ТО': maintenance_cost
    }
    cost_report.update(other_expenses)

    # Загальна сума
    total_cost = sum(cost_report.values())
    cost_report['Загалом'] = total_cost

    total_trips = len(all_trips)

    return render_template(
        'reports.html',
        cost_report={k: float(v) for k, v in cost_report.items()},
        total_trips=total_trips,
        period_report=None
    )


@web_bp.route('/reports/period')
@login_required
def reports_period():
    start = request.args.get('start')
    end = request.args.get('end')

    trips = TripRepository.get_trips_by_period(start, end)

    fuel_total = sum(t.distance_km * t.fuel_cost for t in trips if t.fuel_cost)

    period_report = {
        'trips': len(trips),
        'costs': round(fuel_total, 2)
    }

    all_trips = TripRepository.get_all()
    total_trips = len(all_trips)
    all_expenses = ExpenseRepository().get_all()

    fuel_cost = round(
        sum(float(t.distance_km) * float(t.fuel_cost) for t in all_trips if t.fuel_cost),
        2
    )

    maintenance_cost = round(
        sum(float(e.amount) for e in all_expenses if 'ТО' in e.expense_type),
        2
    )

    total_cost = round(fuel_cost + maintenance_cost, 2)

    cost_report = {
        'Пальне': fuel_cost,
        'ТО': maintenance_cost,
        'Загалом': total_cost
    }

    return render_template(
        'reports.html',
        cost_report=cost_report,
        total_trips=total_trips,
        period_report=period_report
    )


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('web.home'))

    if request.method == 'POST':
        gmail = request.form.get('gmail')
        password = request.form.get('password')

        # Перевірка, чи вже існує користувач
        if User.query.filter_by(username=gmail).first():
            flash('Користувач з таким Gmail вже існує!', 'danger')
            return redirect(url_for('auth.register'))

        # Встановлюємо роль "admin" для всіх
        user = User(username=gmail, role='admin')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)  # автоматичний вхід після реєстрації
        return redirect(url_for('web.home'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('web.home'))

    if request.method == 'POST':
        gmail = request.form.get('gmail')
        password = request.form.get('password')

        user = User.query.filter_by(username=gmail).first()
        if user and user.check_password(password):
            user.role = 'admin'
            db.session.commit()
            login_user(user)

            return redirect(url_for('web.home'))

        flash('Невірний Gmail або пароль', 'danger')
        return redirect(url_for('auth.login'))

    return render_template('login.html')


# ----------------- ВИХІД -----------------
@auth_bp.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash('Ви вийшли з системи', 'success')
    return redirect(url_for('web.home'))


@maintenance_bp.route('/maintenance/edit/<int:maintenance_id>', methods=['GET', 'POST'])
@login_required
def edit(maintenance_id):
    maintenance = MaintenanceRepository.get_by_id(maintenance_id)
    vehicles = VehicleRepository().get_all()

    if request.method == 'POST':
        MaintenanceRepository.update(
            maintenance_id,
            vehicle_id=request.form['vehicle_id'],
            planned_date=request.form['planned_date'],
            maintenance_type=request.form['maintenance_type'],
            cost=request.form['cost']
        )
        flash('ТО оновлено')
        return redirect(url_for('web.maintenance_page'))

    return render_template(
        'edit_maintenance.html',
        maintenance=maintenance,
        vehicles=vehicles
    )


@maintenance_bp.route('/maintenance/delete/<int:maintenance_id>', methods=['POST'])
@login_required
def delete(maintenance_id):
    MaintenanceRepository.delete(maintenance_id)
    flash('ТО видалено')
    return redirect(url_for('web.maintenance_page'))


@web_bp.route('/vehicles/edit/<vehicle_id>', methods=['GET', 'POST'])
@login_required
def edit_vehicle(vehicle_id):
    if current_user.role != 'admin':
        flash("Доступ заборонено!", "danger")
        return redirect(url_for('web.vehicles_page'))

    vehicle = VehicleRepository.get_by_id(vehicle_id)
    if request.method == 'POST':
        VehicleRepository.update(
            vehicle_id,
            brand=request.form['brand'],
            year=request.form['year'],
            vin=request.form['vin'],
            technical_status=request.form['technical_status'],
            mileage=request.form['mileage'],
            insurance_expiry=request.form['insurance_expiry']
        )
        flash("Автомобіль оновлено", "success")
        return redirect(url_for('web.vehicles_page'))

    return render_template('edit_vehicle.html', vehicle=vehicle)


@web_bp.route('/drivers/edit/<driver_id>', methods=['GET', 'POST'])
@login_required
def edit_driver(driver_id):
    if current_user.role != 'admin':
        flash("Доступ заборонено!", "danger")
        return redirect(url_for('web.drivers_page'))

    driver = DriverRepository.get_by_id(driver_id)
    if request.method == 'POST':
        DriverRepository.update(
            driver_id,
            full_name=request.form['full_name'],
            license_number=request.form['license_number'],
            experience_years=request.form['experience_years'],
            medical_check_date=request.form['medical_check_date']
        )
        flash("Водія оновлено", "success")
        return redirect(url_for('web.drivers_page'))

    return render_template('edit_driver.html', driver=driver)


@web_bp.route('/vehicles/delete/<int:vehicle_id>', methods=['GET', 'POST'])
@login_required
def delete_vehicle(vehicle_id):
    if current_user.role != 'admin':
        flash("Доступ заборонено!", "danger")
        return redirect(url_for('web.vehicles_page'))

    MaintenanceRepository.delete_by_vehicle(vehicle_id)
    ExpenseRepository.delete_by_vehicle(vehicle_id)
    VehicleRepository.delete(vehicle_id)

    flash("Автомобіль видалено", "success")
    return redirect(url_for('web.vehicles_page'))


@web_bp.route('/drivers/delete/<int:driver_id>', methods=['GET', 'POST'])
@login_required
def delete_driver(driver_id):
    if current_user.role != 'admin':
        flash("Доступ заборонено!", "danger")
        return redirect(url_for('web.drivers_page'))

    TripRepository.delete_by_driver(driver_id)
    DriverRepository.delete(driver_id)

    flash("Водія та всі його поїздки видалено", "success")
    return redirect(url_for('web.drivers_page'))


# Редагування поїздки
@web_bp.route('/trips/edit/<int:trip_id>', methods=['GET', 'POST'])
@login_required
def edit_trip(trip_id):
    if current_user.role != 'admin':
        flash("Доступ заборонено!", "danger")
        return redirect(url_for('web.trips_page'))

    trip = TripRepository.get_by_id(trip_id)
    drivers = DriverRepository().get_all()
    vehicles = VehicleRepository().get_all()

    if request.method == 'POST':
        TripRepository.update(
            trip_id,
            vehicle_id=int(request.form['vehicle_id']),
            driver_id=int(request.form['driver_id']),
            trip_date=datetime.strptime(request.form['trip_date'], '%Y-%m-%d').date(),
            route=request.form['route'],
            distance_km=float(request.form['distance_km']),
            fuel_cost=float(request.form['fuel_cost'])
        )
        flash("Поїздку оновлено", "success")
        return redirect(url_for('web.trips_page'))

    return render_template('edit_trip.html', trip=trip, drivers=drivers, vehicles=vehicles)


# Видалення поїздки
@web_bp.route('/trips/delete/<int:trip_id>', methods=['POST', 'GET'])
@login_required
def delete_trip(trip_id):
    if current_user.role != 'admin':
        flash("Доступ заборонено!", "danger")
        return redirect(url_for('web.trips_page'))

    TripRepository.delete(trip_id)
    flash("Поїздку видалено", "success")
    return redirect(url_for('web.trips_page'))


@web_bp.route('/notifications')
@login_required
def notifications_page():
    notifications = Notification.query.order_by(Notification.created_at.desc()).all()
    return render_template('notifications.html', notifications=notifications)
