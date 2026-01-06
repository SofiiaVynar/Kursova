from datetime import date, timedelta, datetime
from domain.models import Vehicle, Driver, Maintenance, Notification
from extensions import db
from infrastructure.repositories import DriverRepository, MaintenanceRepository, VehicleRepository


class NotificationService:

    @staticmethod
    def get_vehicle_notifications():
        notes = []
        for m in MaintenanceRepository().get_due():  # теж через екземпляр
            notes.append(f"ТО для автомобіля {m.vehicle_id} заплановане на {m.planned_date}")

        for v in VehicleRepository().get_all():  # <-- тепер працює
            from datetime import date
            if v.insurance_expiry and v.insurance_expiry <= date.today():
                notes.append(f"Страховка для автомобіля {v.id} закінчилась {v.insurance_expiry}")
        return notes

    @staticmethod
    def get_driver_notifications():
        notifications = []

        # Медичний огляд водія
        for d in DriverRepository.get_all():
            if d.medical_check_date <= datetime.today().date():
                notifications.append(f"Медогляд для водія {d.full_name} прострочений або сьогодні")

        return notifications

    @staticmethod
    def get_all_notifications():
        return NotificationService.get_vehicle_notifications() + NotificationService.get_driver_notifications()

